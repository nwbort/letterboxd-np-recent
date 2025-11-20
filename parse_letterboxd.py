#!/usr/bin/env python3
"""
Letterboxd Activity Parser for TRMNL Display
Extracts movie reviews and ratings from Letterboxd HTML
"""

import re
import json
from html.parser import HTMLParser
from datetime import datetime
from typing import List, Dict, Optional


class LetterboxdParser(HTMLParser):
    """Parse Letterboxd activity HTML and extract movie data"""

    def __init__(self):
        super().__init__()
        self.activities = []
        self.current_activity = {}
        self.in_review = False
        self.in_review_body = False
        self.in_title = False
        self.in_rating = False
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Detect activity section
        if tag == 'section' and 'class' in attrs_dict:
            if 'activity-row' in attrs_dict['class']:
                self.current_activity = {}
                self.in_review = True

        # Extract movie title
        if tag == 'h2' and self.in_review and 'class' in attrs_dict:
            if 'name' in attrs_dict['class']:
                self.in_title = True

        # Extract year from release date
        if tag == 'a' and self.in_review and attrs_dict.get('href', '').startswith('/films/year/'):
            year_match = re.search(r'/films/year/(\d{4})/', attrs_dict['href'])
            if year_match:
                self.current_activity['year'] = year_match.group(1)

        # Extract rating
        if tag == 'span' and 'class' in attrs_dict and 'rating' in attrs_dict['class']:
            self.in_rating = True
            # Parse rating class (e.g., "rated-5" means 2.5 stars)
            rating_match = re.search(r'rated-(\d+)', attrs_dict['class'])
            if rating_match:
                rating_value = int(rating_match.group(1))
                stars = rating_value / 2.0
                self.current_activity['rating'] = stars
                self.current_activity['rating_display'] = '★' * int(stars) + ('½' if stars % 1 else '')

        # Extract review text
        if tag == 'div' and 'class' in attrs_dict and 'js-review-body' in attrs_dict['class']:
            self.in_review_body = True

        # Extract timestamp
        if tag == 'time' and 'datetime' in attrs_dict:
            self.current_activity['datetime'] = attrs_dict['datetime']

        # Extract movie link and slug
        if tag == 'a' and self.in_review and 'href' in attrs_dict:
            href = attrs_dict['href']
            # Match pattern like /nicolep/film/wicked-2024/
            if '/film/' in href and href.count('/') >= 3:
                slug_match = re.search(r'/film/([^/]+)/', href)
                if slug_match:
                    self.current_activity['slug'] = slug_match.group(1)
                    self.current_activity['url'] = f"https://letterboxd.com{href}"

    def handle_endtag(self, tag):
        if tag == 'section':
            if self.current_activity and 'title' in self.current_activity:
                self.activities.append(self.current_activity.copy())
            self.current_activity = {}
            self.in_review = False
            self.in_review_body = False

        if tag == 'h2':
            self.in_title = False

        if tag == 'span':
            self.in_rating = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        # Capture movie title
        if self.in_title and data and data not in ['watched', 'rewatched']:
            if 'title' not in self.current_activity:
                self.current_activity['title'] = data

        # Capture review text
        if self.in_review_body:
            if 'review' not in self.current_activity:
                self.current_activity['review'] = data
            else:
                self.current_activity['review'] += ' ' + data


def parse_letterboxd_html(html_content: str) -> List[Dict]:
    """Parse Letterboxd HTML and return list of activities"""
    parser = LetterboxdParser()
    parser.feed(html_content)

    # Clean up and sort activities
    activities = []
    for activity in parser.activities:
        if 'title' in activity:
            # Format date
            if 'datetime' in activity:
                try:
                    dt = datetime.fromisoformat(activity['datetime'].replace('Z', '+00:00'))
                    activity['date'] = dt.strftime('%b %d, %Y')
                    activity['date_short'] = dt.strftime('%b %d')
                except:
                    pass

            # Clean up review text
            if 'review' in activity:
                # Remove translation UI artifacts
                review = activity['review']
                # Remove "Translate" and "Translated from..." text
                review = re.sub(r'\s*Translate\s*Translated from.*$', '', review)
                review = re.sub(r'\s*Translate\s*$', '', review)
                activity['review'] = review.strip()

            activities.append(activity)

    return activities


def format_for_trmnl(activities: List[Dict], limit: int = 5) -> Dict:
    """Format activities for TRMNL merge_variables"""

    # Get most recent activities with reviews
    recent = activities[:limit]

    # Format for TRMNL
    merge_vars = {
        'user': 'NicoleP',
        'update_time': datetime.now().strftime('%b %d, %Y %I:%M %p'),
        'movies': []
    }

    for activity in recent:
        movie_data = {
            'title': activity.get('title', ''),
            'year': activity.get('year', ''),
            'rating': activity.get('rating', 0),
            'rating_display': activity.get('rating_display', ''),
            'review': activity.get('review', ''),
            'date': activity.get('date', ''),
            'date_short': activity.get('date_short', ''),
            'url': activity.get('url', '')
        }
        merge_vars['movies'].append(movie_data)

    # Add summary stats
    merge_vars['total_activities'] = len(recent)

    # Get latest movie for prominent display
    if recent:
        latest = recent[0]
        merge_vars['latest_title'] = latest.get('title', '')
        merge_vars['latest_year'] = latest.get('year', '')
        merge_vars['latest_rating'] = latest.get('rating_display', '')
        merge_vars['latest_review'] = latest.get('review', '')
        merge_vars['latest_date'] = latest.get('date', '')

    return {'merge_variables': merge_vars}


def main():
    """Main function to parse and format Letterboxd data"""

    # Read HTML file
    html_file = 'letterboxd.com-ajax-activity-pagination-NicoleP.html'

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: {html_file} not found")
        return

    # Parse activities
    activities = parse_letterboxd_html(html_content)

    print(f"\n📽️  Found {len(activities)} movie activities\n")
    print("=" * 80)

    # Display parsed activities
    for i, activity in enumerate(activities, 1):
        print(f"\n{i}. {activity.get('title', 'Unknown')} ({activity.get('year', 'N/A')})")
        if 'rating_display' in activity:
            print(f"   Rating: {activity['rating_display']} ({activity.get('rating', 0)} stars)")
        if 'review' in activity:
            review = activity['review']
            if len(review) > 100:
                review = review[:100] + '...'
            print(f"   Review: {review}")
        if 'date' in activity:
            print(f"   Date: {activity['date']}")

    print("\n" + "=" * 80)

    # Format for TRMNL
    trmnl_data = format_for_trmnl(activities, limit=5)

    # Save to JSON file
    output_file = 'letterboxd_trmnl_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trmnl_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ TRMNL data saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   - Total activities parsed: {len(activities)}")
    print(f"   - Activities in TRMNL output: {trmnl_data['merge_variables']['total_activities']}")
    if 'latest_title' in trmnl_data['merge_variables']:
        print(f"   - Latest movie: {trmnl_data['merge_variables']['latest_title']} ({trmnl_data['merge_variables']['latest_year']})")


if __name__ == '__main__':
    main()

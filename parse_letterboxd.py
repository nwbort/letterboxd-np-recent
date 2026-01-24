#!/usr/bin/env python3
"""
Letterboxd Activity Parser for TRMNL Display
Extracts movie reviews and ratings from Letterboxd RSS feed
"""

import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from html import unescape


def parse_rating_display(rating: float) -> str:
    """Convert numeric rating to star display (e.g., 4.5 -> ★★★★½)"""
    full_stars = int(rating)
    half_star = '½' if (rating % 1) >= 0.5 else ''
    return '★' * full_stars + half_star


def extract_review_from_description(description: str) -> str:
    """Extract review text from CDATA description HTML"""
    if not description:
        return ''

    # Remove HTML tags
    text = re.sub(r'<img[^>]*>', '', description)  # Remove images
    text = re.sub(r'<p>', '', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)  # Remove any other tags

    # Unescape HTML entities
    text = unescape(text)

    # Clean up whitespace
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

    # Filter out "Watched on..." lines that have no review
    if text.startswith('Watched on '):
        return ''

    return text.strip()


def parse_letterboxd_rss(xml_content: str) -> List[Dict]:
    """Parse Letterboxd RSS feed and return list of activities"""

    # Parse XML
    root = ET.fromstring(xml_content)

    # Define namespaces
    namespaces = {
        'letterboxd': 'https://letterboxd.com',
        'tmdb': 'https://themoviedb.org',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    activities = []

    # Find all items in the RSS feed
    for item in root.findall('.//item'):
        activity = {}

        # Extract film title and year from letterboxd namespace
        film_title = item.find('letterboxd:filmTitle', namespaces)
        film_year = item.find('letterboxd:filmYear', namespaces)

        if film_title is not None:
            activity['title'] = film_title.text
        if film_year is not None:
            activity['year'] = film_year.text

        # Extract link/URL
        link = item.find('link')
        if link is not None and link.text:
            activity['url'] = link.text
            # Extract slug from URL (e.g., "hamnet" from "/nicolep/film/hamnet/")
            slug_match = re.search(r'/film/([^/]+)/', link.text)
            if slug_match:
                activity['slug'] = slug_match.group(1)

        # Extract rating
        member_rating = item.find('letterboxd:memberRating', namespaces)
        if member_rating is not None and member_rating.text:
            try:
                rating_value = float(member_rating.text)
                activity['rating'] = rating_value
                activity['rating_display'] = parse_rating_display(rating_value)
            except ValueError:
                pass

        # Extract watched date
        watched_date = item.find('letterboxd:watchedDate', namespaces)
        if watched_date is not None and watched_date.text:
            activity['datetime'] = watched_date.text
            try:
                dt = datetime.fromisoformat(watched_date.text)
                activity['date'] = dt.strftime('%b %d, %Y')
                activity['date_short'] = dt.strftime('%b %d')
            except:
                pass

        # Extract review from description
        description = item.find('description')
        if description is not None and description.text:
            review = extract_review_from_description(description.text)
            if review:
                activity['review'] = review

        # Only add if we have a title
        if 'title' in activity:
            activities.append(activity)

    return activities


def format_for_trmnl(activities: List[Dict], limit: int = 5) -> Dict:
    """Format activities for TRMNL merge_variables"""

    # Get most recent activities
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

    # Read RSS/XML file - look for .xml file
    import glob
    xml_files = glob.glob('letterboxd.com-NicoleP-rss.xml')
    if not xml_files:
        # Fallback to old naming
        xml_files = glob.glob('letterboxd.com-*.xml')

    if not xml_files:
        print("Error: No Letterboxd XML/RSS file found")
        print("Expected: letterboxd.com-NicoleP-rss.xml")
        return

    xml_file = xml_files[0]

    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
    except FileNotFoundError:
        print(f"Error: {xml_file} not found")
        return

    # Parse activities
    activities = parse_letterboxd_rss(xml_content)

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

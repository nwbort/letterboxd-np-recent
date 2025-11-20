# 🎬 Letterboxd TRMNL Integration

Display your recent Letterboxd movie reviews on your TRMNL e-ink display!

## What This Does

This project scrapes your Letterboxd activity and formats it for display on a TRMNL device. It extracts:
- Movie titles and years
- Your ratings (star ratings)
- Review text
- Watch dates

## Quick Start

### 1. Update the Data

Run the update script to fetch latest activity and generate the JSON file:

```bash
./update_trmnl.sh
```

This will:
1. Download latest activity from Letterboxd
2. Parse the HTML to extract movie data
3. Generate `letterboxd_trmnl_data.json` in TRMNL format

### 2. Serve the JSON File

You need to make the JSON file accessible to TRMNL. Options:

#### Option A: Simple HTTP Server (for testing)

```bash
python3 -m http.server 8000
```

The JSON will be available at: `http://your-ip:8000/letterboxd_trmnl_data.json`

#### Option B: Use the Flask Server

```bash
python3 trmnl_server.py
```

Access at: `http://your-ip:5000/api/plugin`

#### Option C: Host on a web server

Upload `letterboxd_trmnl_data.json` to any web server (GitHub Pages, your own server, etc.)

### 3. Configure TRMNL

1. Go to your TRMNL dashboard at [usetrmnl.com](https://usetrmnl.com)
2. Create a new **Private Plugin**
3. Choose **"Polling Strategy"**
4. Set your endpoint URL (e.g., `http://your-server:8000/letterboxd_trmnl_data.json`)
5. Copy the HTML template content from `templates/full_screen.html`
6. Paste it into the TRMNL markup editor
7. Save and activate!

## Files Overview

```
.
├── download.sh                          # Download script for any URL
├── scrape.sh                            # Downloads Letterboxd activity
├── update_trmnl.sh                      # One-command update script
├── parse_letterboxd.py                  # Python parser
├── trmnl_server.py                      # Optional Flask server
├── letterboxd_trmnl_data.json          # Generated TRMNL data
└── templates/
    ├── full_screen.html                 # Full screen template (800x480)
    └── half_horizontal.html             # Half screen template (800x240)
```

## Data Format

The generated JSON follows TRMNL's merge_variables format:

```json
{
  "merge_variables": {
    "user": "NicoleP",
    "update_time": "Nov 20, 2025 01:31 AM",
    "latest_title": "Wicked",
    "latest_year": "2024",
    "latest_rating": "★★½",
    "latest_review": "People who enjoy musicals need to be so fr...",
    "latest_date": "Nov 18, 2025",
    "movies": [
      {
        "title": "Wicked",
        "year": "2024",
        "rating": 2.5,
        "rating_display": "★★½",
        "review": "...",
        "date": "Nov 18, 2025",
        "url": "https://letterboxd.com/..."
      }
    ]
  }
}
```

## Available Template Variables

Use these in your TRMNL markup templates:

### Single Values
- `{{ user }}` - Letterboxd username
- `{{ update_time }}` - Last update timestamp
- `{{ latest_title }}` - Most recent movie title
- `{{ latest_year }}` - Year of latest movie
- `{{ latest_rating }}` - Star rating display (★★★½)
- `{{ latest_review }}` - Review text
- `{{ latest_date }}` - Watch date
- `{{ total_activities }}` - Number of activities

### Array (loop through)
```liquid
{% for movie in movies %}
  {{ movie.title }}
  {{ movie.year }}
  {{ movie.rating_display }}
  {{ movie.review }}
  {{ movie.date }}
{% endfor %}
```

## Automation

### Cron Job (Linux/Mac)

Update every hour:

```bash
crontab -e
```

Add:
```
0 * * * * cd /path/to/letterboxd-np-recent && ./update_trmnl.sh >> /tmp/trmnl-update.log 2>&1
```

### GitHub Actions

For automated updates with GitHub Pages hosting, create `.github/workflows/update.yml`:

```yaml
name: Update Letterboxd Data
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Update data
        run: ./update_trmnl.sh
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add letterboxd_trmnl_data.json
          git commit -m "Update Letterboxd data" || exit 0
          git push
```

## Customization

### Change User

Edit `scrape.sh` and `parse_letterboxd.py` to change the username from "NicoleP" to your Letterboxd username.

### Adjust Display

Modify the HTML templates in `templates/` to customize:
- Font sizes
- Layout
- Number of movies shown
- Which data is displayed

### Change Update Frequency

TRMNL lets you set polling frequency:
- Minimum: Every 15 minutes
- Maximum: Once per day

## Troubleshooting

**No data appearing?**
- Check that `letterboxd_trmnl_data.json` exists and has content
- Verify your server is accessible from the internet
- Check TRMNL plugin logs for errors

**Review text looks weird?**
- The parser tries to clean up HTML artifacts
- You may need to adjust the regex in `parse_letterboxd.py`

**Old data showing?**
- Make sure you're running `update_trmnl.sh` regularly
- Check that TRMNL is polling at the right frequency

## Resources

- [TRMNL Documentation](https://docs.usetrmnl.com)
- [Letterboxd API](https://letterboxd.com/api-beta/)
- [Liquid Templating](https://shopify.github.io/liquid/)

## License

This is a personal project for educational purposes. Letterboxd data belongs to the user and Letterboxd.

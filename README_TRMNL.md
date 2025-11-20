# 🎬 Letterboxd → TRMNL Auto-Update

Automatically display your latest Letterboxd movie reviews on your TRMNL e-ink display, updated every 2 hours via GitHub Actions!

## 🚀 Quick Setup (5 minutes)

### Step 1: Enable GitHub Actions

1. Go to your repository Settings
2. Navigate to **Actions** → **General**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Click **Save**

### Step 2: Enable GitHub Pages

1. Go to Settings → **Pages**
2. Under "Source", select **"GitHub Actions"**
3. Click **Save**
4. Your site will be published at: `https://[username].github.io/[repo-name]/`

### Step 3: Trigger First Update

1. Go to the **Actions** tab
2. Click **"Update Letterboxd Data"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait ~30 seconds for completion
5. The **"Deploy to GitHub Pages"** workflow will run automatically

### Step 4: Configure TRMNL

1. Go to [TRMNL Dashboard](https://usetrmnl.com)
2. Click **"Add Plugin"** → **"Private Plugin"**
3. Choose **"Polling Strategy"**
4. Enter your endpoint URL:
   ```
   https://[username].github.io/[repo-name]/letterboxd_trmnl_data.json
   ```
5. Copy the template from `templates/full_screen.html`
6. Paste into the TRMNL **Markup** editor
7. **Save** and activate!

## 📁 What's Included

```
📦 Repository
├── 🤖 .github/workflows/
│   ├── update-letterboxd.yml    # Auto-updates data every 2 hours
│   └── pages.yml                 # Deploys JSON to GitHub Pages
├── 📄 parse_letterboxd.py        # Python parser
├── 📥 download.sh                # Download script
├── 🎨 templates/
│   ├── full_screen.html          # Full screen layout (800x480)
│   └── half_horizontal.html      # Half screen layout (800x240)
├── 📊 letterboxd_trmnl_data.json # Generated data (auto-updated)
└── 📖 README_TRMNL.md           # This file
```

## ⚙️ How It Works

### Automatic Updates

The GitHub Action:
1. **Runs every 2 hours** (customizable in `update-letterboxd.yml`)
2. Downloads latest activity from Letterboxd
3. Parses HTML → extracts movies, ratings, reviews
4. Generates `letterboxd_trmnl_data.json`
5. Commits changes if data changed
6. Deploys to GitHub Pages

### TRMNL Polling

Your TRMNL device:
1. Polls your GitHub Pages URL
2. Receives JSON with `merge_variables`
3. Renders the HTML template with your data
4. Displays on the e-ink screen

## 🎨 Customization

### Change Update Frequency

Edit `.github/workflows/update-letterboxd.yml`:

```yaml
schedule:
  - cron: '0 */2 * * *'  # Every 2 hours
  # - cron: '0 * * * *'  # Every hour
  # - cron: '0 */6 * * *'  # Every 6 hours
```

[Cron schedule reference](https://crontab.guru/)

### Change Username

Edit `scrape.sh` line 2:

```bash
./download.sh 'https://letterboxd.com/ajax/activity-pagination/YOUR_USERNAME/'
```

Also update in:
- `.github/workflows/update-letterboxd.yml` (line with download.sh)
- `parse_letterboxd.py` (line 154: `'user': 'YOUR_USERNAME'`)

### Customize Display

Edit templates in `templates/`:

**Full Screen (800x480px)**
- `templates/full_screen.html`
- Shows featured movie + recent list
- Ideal for single plugin display

**Half Screen (800x240px)**
- `templates/half_horizontal.html`
- Shows latest movie only
- For split screen layouts

## 📊 Data Structure

The JSON follows TRMNL's format:

```json
{
  "merge_variables": {
    "user": "NicoleP",
    "update_time": "Nov 20, 2025 01:31 AM",
    "latest_title": "Wicked",
    "latest_year": "2024",
    "latest_rating": "★★½",
    "latest_review": "People who enjoy musicals...",
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

## 🔧 Template Variables

Use these in your TRMNL markup:

### Single Values
```liquid
{{ user }}              - Username
{{ update_time }}       - Last update
{{ latest_title }}      - Latest movie
{{ latest_year }}       - Year
{{ latest_rating }}     - Stars (★★★½)
{{ latest_review }}     - Review text
{{ latest_date }}       - Date watched
{{ total_activities }}  - Count
```

### Loop Through Movies
```liquid
{% for movie in movies %}
  <div>
    <h3>{{ movie.title }} ({{ movie.year }})</h3>
    <p>{{ movie.rating_display }}</p>
    <p>{{ movie.review }}</p>
    <small>{{ movie.date }}</small>
  </div>
{% endfor %}
```

## 🐛 Troubleshooting

### ❌ Actions failing?

**Error: "Permission denied"**
- Go to Settings → Actions → General
- Enable "Read and write permissions"

**Error: "Resource not accessible"**
- Check that workflows are enabled in Actions tab
- Verify branch name (main vs master)

### ❌ Pages not deploying?

**404 on GitHub Pages URL**
- Wait 2-3 minutes after first deployment
- Check Settings → Pages shows green checkmark
- Verify Actions tab shows successful deployment

**JSON not updating**
- Check Actions tab for workflow runs
- Look for errors in workflow logs
- Manually trigger "Update Letterboxd Data"

### ❌ TRMNL not showing data?

**No content displayed**
- Verify JSON URL is accessible (open in browser)
- Check TRMNL plugin settings
- Review template syntax in markup editor
- Look for errors in TRMNL logs

**Old data showing**
- Check GitHub Actions ran successfully
- Verify JSON file was updated (check commit time)
- TRMNL polls every 15 min - 1 hour depending on settings

## 📚 Resources

- [TRMNL Documentation](https://docs.usetrmnl.com)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Liquid Templating](https://shopify.github.io/liquid/)
- [Letterboxd](https://letterboxd.com)

## 🎯 Advanced Options

### Add More Users

Create multiple JSON files:

1. Duplicate workflow for each user
2. Change output filename
3. Parse different Letterboxd URLs
4. Create separate TRMNL plugins

### Use a Custom Domain

1. Add CNAME file to public directory in Pages workflow
2. Configure DNS at your provider
3. Update TRMNL plugin URL

### Local Development

Run locally to test:

```bash
# Update data
./update_trmnl.sh

# Serve locally
python3 trmnl_server.py

# Preview at http://localhost:5000/preview
```

## 📝 License

MIT - Feel free to modify and reuse!

---

Made with ❤️ for TRMNL and Letterboxd users

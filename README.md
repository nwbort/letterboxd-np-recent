# 🎬 Letterboxd → TRMNL Auto-Update

Automatically display your latest Letterboxd movie reviews on your TRMNL e-ink display!

Updates every 2 hours via GitHub Actions → serves via raw GitHub URL.

## 🚀 Quick Setup (2 minutes)

### Step 1: Enable GitHub Actions

1. Go to your repository **Settings**
2. Navigate to **Actions** → **General**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Click **Save**

### Step 2: Run First Update

1. Go to the **Actions** tab
2. Click **"Update Letterboxd Data"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait ~30 seconds for completion

### Step 3: Get Your Raw URL

Your TRMNL endpoint URL will be:

```
https://raw.githubusercontent.com/[username]/[repo-name]/[branch]/letterboxd_trmnl_data.json
```

Example:
```
https://raw.githubusercontent.com/nwbort/letterboxd-np-recent/main/letterboxd_trmnl_data.json
```

### Step 4: Configure TRMNL

1. Go to [TRMNL Dashboard](https://usetrmnl.com)
2. Click **"Add Plugin"** → **"Private Plugin"**
3. Choose **"Polling Strategy"**
4. Paste your raw GitHub URL (from Step 3)
5. Copy template content from `templates/full_screen.html`
6. Paste into the TRMNL **Markup** editor
7. **Save** and activate!

## ⚙️ How It Works

1. **GitHub Action runs every 2 hours**
2. Downloads the latest Letterboxd RSS feed (`scrape.sh`) — this file is scratch input, never committed
3. Parses it into movies, ratings, reviews
4. Updates `letterboxd_trmnl_data.json` (only bumping the timestamp if the data actually changed)
5. Commits `letterboxd_trmnl_data.json` to the repository
6. TRMNL polls the raw GitHub URL

## 🎨 Customize

### Change Username

Edit `scrape.sh`:

```bash
./download.sh 'https://letterboxd.com/YOUR_USERNAME/rss/'
```

Also update `parse_letterboxd.py`:
```python
'user': 'YOUR_USERNAME',
```

### Change Update Frequency

Edit `.github/workflows/update-letterboxd.yml` line 5:

```yaml
schedule:
  - cron: '0 */2 * * *'  # Every 2 hours (current)
  # - cron: '0 * * * *'  # Every hour
  # - cron: '0 */6 * * *'  # Every 6 hours
```

[Cron schedule helper](https://crontab.guru/)

### Customize Display

Edit templates in `templates/`:
- `full_screen.html` - Full screen (800x480)
- `half_horizontal.html` - Half screen (800x240)

## 📊 Template Variables

Use these in your TRMNL markup:

```liquid
{{ user }}              - Username
{{ update_time }}       - Last update timestamp
{{ latest_title }}      - Most recent movie
{{ latest_year }}       - Year
{{ latest_rating }}     - Stars (★★★½)
{{ latest_review }}     - Review text
{{ latest_date }}       - Date watched
{{ total_activities }}  - Number of activities

{% for movie in movies %}
  {{ movie.title }}
  {{ movie.rating_display }}
  {{ movie.review }}
{% endfor %}
```

## 🐛 Troubleshooting

**Actions not running?**
- Enable "Read and write permissions" in Settings → Actions
- Check Actions tab for error logs
- Manually trigger workflow

**TRMNL shows nothing?**
- Verify raw URL loads in browser
- Check template syntax
- Wait for TRMNL's next poll (15min - 1hr)

**Old data showing?**
- Check Actions tab - workflow ran successfully?
- Look at latest commit time
- Verify branch name in raw URL matches repo

## 📝 Files

- `.github/workflows/update-letterboxd.yml` - Auto-update workflow
- `parse_letterboxd.py` - Parser script
- `download.sh` - Download script
- `templates/` - Display templates
- `letterboxd_trmnl_data.json` - Generated data (auto-updated)

## 🔗 Resources

- [TRMNL Docs](https://docs.usetrmnl.com)
- [Letterboxd](https://letterboxd.com)
- [Liquid Templating](https://shopify.github.io/liquid/)

---

Made for TRMNL + Letterboxd 🎬

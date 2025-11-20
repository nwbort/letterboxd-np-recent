#!/usr/bin/env python3
"""
TRMNL Server for Letterboxd Activity
Serves parsed Letterboxd data in TRMNL-compatible format
"""

from flask import Flask, jsonify, request, render_template_string
import json
import os
from datetime import datetime
from parse_letterboxd import parse_letterboxd_html, format_for_trmnl

app = Flask(__name__)

# Load templates
def load_template(template_name):
    """Load HTML template file"""
    template_path = os.path.join('templates', template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def get_latest_data():
    """Parse latest Letterboxd HTML and return formatted data"""
    html_file = 'letterboxd.com-ajax-activity-pagination-NicoleP.html'

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        return None

    activities = parse_letterboxd_html(html_content)
    return format_for_trmnl(activities, limit=5)


@app.route('/')
def index():
    """Home page with API documentation"""
    return """
    <html>
    <head>
        <title>Letterboxd TRMNL Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 { color: #333; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
            }
            pre {
                background: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .endpoint {
                background: #e8f4f8;
                padding: 15px;
                margin: 20px 0;
                border-left: 4px solid #0066cc;
            }
        </style>
    </head>
    <body>
        <h1>🎬 Letterboxd TRMNL Server</h1>
        <p>This server provides Letterboxd activity data for TRMNL devices.</p>

        <div class="endpoint">
            <h2>GET /api/plugin</h2>
            <p>Main TRMNL plugin endpoint</p>
            <p>Returns: JSON with <code>merge_variables</code> containing movie data</p>
            <p><a href="/api/plugin">Try it →</a></p>
        </div>

        <div class="endpoint">
            <h2>GET /api/data</h2>
            <p>Raw activity data endpoint</p>
            <p>Returns: JSON with <code>merge_variables</code> containing movie data</p>
            <p><a href="/api/data">Try it →</a></p>
        </div>

        <div class="endpoint">
            <h2>GET /preview</h2>
            <p>Preview full-screen TRMNL display</p>
            <p><a href="/preview">Try it →</a></p>
        </div>

        <div class="endpoint">
            <h2>GET /preview/half</h2>
            <p>Preview half-screen TRMNL display</p>
            <p><a href="/preview/half">Try it →</a></p>
        </div>

        <h2>TRMNL Integration</h2>
        <p>To integrate with your TRMNL device:</p>
        <ol>
            <li>Go to your TRMNL dashboard</li>
            <li>Create a new Private Plugin with "Polling Strategy"</li>
            <li>Set the endpoint URL to: <code>http://your-server:5000/api/plugin</code></li>
            <li>Copy the template HTML from <code>/templates/</code> into the markup editor</li>
            <li>Variables like <code>{{ latest_title }}</code> will be populated automatically</li>
        </ol>

        <h2>Webhook Integration</h2>
        <p>For webhook-based updates:</p>
        <pre>curl -X POST http://your-trmnl-webhook-url \\
  -H "Content-Type: application/json" \\
  -d @letterboxd_trmnl_data.json</pre>
    </body>
    </html>
    """


@app.route('/api/plugin', methods=['GET', 'POST'])
def plugin_endpoint():
    """
    Main TRMNL plugin endpoint
    Accepts GET (polling) or POST (webhook) requests
    """
    data = get_latest_data()

    if data is None:
        return jsonify({'error': 'No data available'}), 404

    # Log request for debugging
    print(f"[{datetime.now()}] Plugin endpoint called")
    print(f"  Method: {request.method}")
    if request.method == 'POST':
        print(f"  Body: {request.get_json()}")

    return jsonify(data)


@app.route('/api/data')
def data_endpoint():
    """Return raw data as JSON"""
    data = get_latest_data()

    if data is None:
        return jsonify({'error': 'No data available'}), 404

    return jsonify(data)


@app.route('/preview')
def preview_full():
    """Preview the full-screen template with real data"""
    data = get_latest_data()
    if data is None:
        return "No data available", 404

    template = load_template('full_screen.html')
    if template is None:
        return "Template not found", 404

    # Render template with Jinja2 (simulating Liquid templating)
    from jinja2 import Template
    jinja_template = Template(template)
    rendered = jinja_template.render(**data['merge_variables'])

    return rendered


@app.route('/preview/half')
def preview_half():
    """Preview the half-screen template with real data"""
    data = get_latest_data()
    if data is None:
        return "No data available", 404

    template = load_template('half_horizontal.html')
    if template is None:
        return "Template not found", 404

    from jinja2 import Template
    jinja_template = Template(template)
    rendered = jinja_template.render(**data['merge_variables'])

    return rendered


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    # Check if data file exists
    if not os.path.exists('letterboxd.com-ajax-activity-pagination-NicoleP.html'):
        print("Warning: letterboxd.com-ajax-activity-pagination-NicoleP.html not found")
        print("Run ./scrape.sh first to download the data")

    print("\n🎬 Letterboxd TRMNL Server Starting...")
    print("=" * 60)
    print("Server will be available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  - http://localhost:5000/           (Documentation)")
    print("  - http://localhost:5000/api/plugin  (TRMNL Plugin)")
    print("  - http://localhost:5000/api/data    (Raw Data)")
    print("  - http://localhost:5000/preview     (Full Screen)")
    print("  - http://localhost:5000/preview/half (Half Screen)")
    print("=" * 60)
    print("\n")

    app.run(host='0.0.0.0', port=5000, debug=True)

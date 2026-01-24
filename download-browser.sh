#!/usr/bin/env bash
#
# download-browser.sh - Downloads using headless browser to bypass Cloudflare
# Usage: ./download-browser.sh URL [OUTPUT_FILE]

set -e

# Check if URL provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 URL [OUTPUT_FILE]"
  exit 1
fi

URL="$1"
OUTPUT_FILE="${2:-output.html}"

# Check if shot-scraper is available
if ! command -v shot-scraper &> /dev/null; then
  echo "Error: shot-scraper is not installed"
  echo "Install with: pip install shot-scraper && shot-scraper install"
  exit 1
fi

# Download using shot-scraper (bypasses Cloudflare)
echo "Downloading $URL using headless browser..."
shot-scraper html "$URL" -o "$OUTPUT_FILE" --wait 2000

echo "Downloaded to: $OUTPUT_FILE"

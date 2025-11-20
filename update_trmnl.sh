#!/bin/bash
#
# Update TRMNL data - Download latest Letterboxd activity and generate JSON
#

set -e

echo "🎬 Updating Letterboxd data for TRMNL..."
echo "=========================================="

# Download latest activity
echo "📥 Downloading latest activity from Letterboxd..."
./download.sh 'https://letterboxd.com/ajax/activity-pagination/NicoleP/'

# Parse and generate TRMNL JSON
echo "🔍 Parsing HTML and generating TRMNL data..."
python3 parse_letterboxd.py

echo ""
echo "✅ Update complete!"
echo ""
echo "📊 JSON file ready at: letterboxd_trmnl_data.json"
echo "🌐 You can now configure TRMNL to poll this file"

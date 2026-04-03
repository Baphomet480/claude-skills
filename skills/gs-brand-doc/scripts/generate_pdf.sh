#!/bin/bash
# scripts/generate_pdf.sh

if [ -z "$1" ]; then
  echo "Usage: bash generate_pdf.sh <input.md>"
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${INPUT_FILE%.md}.pdf"

# Resolve absolute path to the CSS file in the skill's assets folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSS_PATH="$SCRIPT_DIR/../assets/gs-brand.css"

echo "Generating PDF for $INPUT_FILE using Generic Service branding..."

# Use npx to run md-to-pdf without installing it globally
# We pass the CSS, and also set up header/footer to include the GS mark
npx -y md-to-pdf "$INPUT_FILE" \
  --launch-options '{ "args": ["--no-sandbox", "--disable-setuid-sandbox"] }' \
  --stylesheet "$CSS_PATH" \
  --pdf-options '{ "format": "Letter", "margin": {"top": "25mm", "right": "20mm", "bottom": "25mm", "left": "20mm"}, "displayHeaderFooter": true, "headerTemplate": "<div style=\"font-size: 10px; width: 100%; padding: 0 20mm 10px 20mm; text-align: right; color: #808080; font-family: monospace;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgdmlld0JveD0iMCAwIDUxMiA1MTIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3Qgd2lkdGg9IjUxMiIgaGVpZ2h0PSI1MTIiIGZpbGw9IiMwQTBBMEEiIHJ4PSIwIi8+CiAgPHBhdGggZD0iTTY1Ljc5IDM1MC4zOVYxODUuMTZIMTIwLjgwVjE5OS41MUg4Mi4zNVYzMzYuMDRIMTIwLjgwVjM1MC4zOVoiIGZpbGw9IiNENEE4NDMiLz4KICA8cGF0aCBkPSJNNDQ2LjIxIDE4NS4xNlYzNTAuMzlIMzkxLjIwVjMzNi4wNEg0MjkuNjVWMTk5LjUxSDM5MS4yMFYxODUuMTZaIiBmaWxsPSIjRDRBODQzIi8+CiAgPHBhdGggZD0iTTIyMi4yMiAzMDcuMzRIMjIwLjkzUTIxOS4yOCAzMTEuMjAgMjE2Ljk4IDMxNC43OVEyMTQuNjggMzE4LjM4IDIxMS4yNyAzMjEuMTRRMjA3Ljg3IDMyMy45MCAyMDMuMDggMzI1LjU1UTE5OC4zMCAzMjcuMjEgMTkyLjA0IDMyNy4yMVExNzEuOTkgMzI3LjIxIDE2MS44NyAzMTAuMTBRMTUxLjc1IDI5Mi45OCAxNTEuNzUgMjYxLjcwUTE1MS43NSAyMjguOTUgMTYzLjM0IDIxMS42NlExNzQuOTMgMTk0LjM2IDE5OC44NSAxOTQuMzZRMjA4LjI0IDE5NC4zNiAyMTUuMzIgMTk2Ljk0UTIyMi40MCAxOTkuNTEgMjI3LjM3IDIwMy44NFEyMzIuMzQgMjA4LjE2IDIzNS42NSAyMTMuOTZRMjM4Ljk2IDIxOS43NSAyNDAuOTkgMjI2LjE5TDIyMi40MCAyMzIuNDVRMjIwLjkzIDIyOC4yMiAyMTkuMDkgMjI0LjQ0UTIxNy4yNSAyMjAuNjcgMjE0LjU4IDIxNy43M1EyMTEuOTIgMjE0Ljc4IDIwOC4xNCAyMTMuMTNRMjA0LjM3IDIxMS40NyAxOTkuMDQgMjExLjQ3UTE4NS42MCAyMTEuNDcgMTc5LjYyIDIyMS44N1ExNzMuNjQgMjMyLjI2IDE3My42NCAyNDkuOTNWMjcwLjM1UTE3My42NCAyNzkuMTggMTc0LjkzIDI4Ni41NFExNzYuMjIgMjkzLjkwIDE3OS4yNiAyOTkuMTVRMTgyLjI5IDMwNC4zOSAxODcuMTcgMzA3LjM0UTE5Mi4wNCAzMTAuMjggMTk5LjA0IDMxMC4yOFEyMTAuMjYgMzEwLjI4IDIxNi4yNCAzMDMuNTZRMjIyLjIyIDI5Ni44NSAyMjIuMjIgMjg2LjM2VjI3NC43N0gxOTcuMzhWMjU5LjMxSDI0MC45OVYzMjUuMDBIMjIyLjIyWiIgZmlsbD0iI0Y1RjBFQiIvPgogIDxwYXRoIGQ9Ik0zMTIuNjAgMzI3LjIxUTI5NS44NSAzMjcuMjEgMjg0LjQ0IDMyMS4zMlEyNzMuMDQgMzE1LjQzIDI2NS42OCAzMDUuNjhMMjc4LjkyIDI5Mi45OFEyODYuMjggMzAxLjgyIDI5NC41NiAzMDUuOTZRMzAyLjg0IDMxMC4xMCAzMTMuMzMgMzEwLjEwUTMyNS40OCAzMTAuMTAgMzMyLjAxIDMwNC41OFEzMzguNTQgMjk5LjA2IDMzMy41NCAyODguNzVRMzM4LjU0IDI4MC40NyAzMzMuNzYgMjc1Ljk2UTMyOC45NyAyNzEuNDYgMzE3LjM4IDI2OS40M0wzMDMuNDAgMjY3LjIyUTI5NC4yMCAyNjUuNzUgMjg3Ljk0IDI2Mi4zNVEyODEuNjggMjU4Ljk0IDI3Ny44MiAyNTQuMjVRMjczLjk2IDI0OS41NiAyNzIuMjEgMjQzLjc2UTI3MC40NiAyMzcuOTcgMjcwLjQ2IDIzMS41M1EyNzAuNDYgMjEzLjMxIDI4Mi4yNCAyMDMuODRRMjk0LjAxIDE5NC4zNiAzMTQuNjIgMTk0LjM2UTMyOS44OSAxOTQuMzYgMzQwLjY2IDE5OS4yNFEzNTEuNDIgMjA0LjExIDM1OC4wNCAyMTIuOTRMMzQ1LjE2IDIyNS44MlEzMzkuODMgMjE5LjM4IDMzMi41NiAyMTUuNDNRMzI1LjI5IDIxMS40NyAzMTQuNjIgMjExLjQ3UTMwMy4yMSAyMTEuNDcgMjk3LjIzIDIxNi4zNVEyOTEuMjUgMjIxLjIyIDI5MS4yNSAyMzAuNjFRMjkxLjI1IDIzOC41MiAyOTUuOTQgMjQzLjAzUTMwMC42NCAyNDcuNTQgMzEyLjYwIDI0OS41NkwzMjYuMjEgMjUxLjk1UTM0My41MSAyNTUuMDggMzUxLjQyIDI2NC41NlEzNTkuMzMgMjc0LjAzIDM1OS4zMyAyODcuNjVRMzU5LjMzIDI5Ni40OCAzNTYuMzAgMzAzLjg0UTM1My4yNiAzMTEuMjAgMzQ3LjI4IDMxNi4zNVEzNDEuMzAgMzIxLjUwIDMzMi41NiAzMjQuMzZRMzIzLjgyIDMyNy4yMSAzMTIuNjAgMzI3LjIxWiIgZmlsbD0iI0Y1RjBFQiIvPgo8L3N2Zz4=\" style=\"height: 14px; vertical-align: middle;\"></div>", "footerTemplate": "<div style=\"font-size: 10px; width: 100%; padding: 10px 20mm 0 20mm; text-align: center; color: #808080; font-family: monospace;\"><span class=\"pageNumber\"></span> / <span class=\"totalPages\"></span></div>" }'

if [ $? -eq 0 ]; then
  echo "✅ Successfully generated: $OUTPUT_FILE"
else
  echo "❌ Error generating PDF."
  exit 1
fi

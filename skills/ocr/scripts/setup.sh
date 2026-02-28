#!/usr/bin/env bash
set -e

echo "Installing system dependencies (sudo required)..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-osd  ocrmypdf poppler-utils imagemagick ghostscript

echo "Setting up Python virtual environment with uv at ~/.local-ocr..."
uv venv ~/.local-ocr
# Using pip from the virtualenv
~/.local-ocr/bin/uv pip install -r "$(dirname "$0")/requirements.txt"

echo "Setup complete!"
echo "You can now use: uv run --project ~/.local-ocr scripts/ocr.py <command>"

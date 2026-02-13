#!/usr/bin/env python3
"""Fetch web page content using Playwright to bypass Cloudflare and render SPAs.

Usage:
    python3 fetch-page.py <url> [--selector CSS_SELECTOR] [--wait SECONDS] [--codepen-code]

Examples:
    # Fetch a CodePen pen page and extract code
    python3 fetch-page.py "https://codepen.io/mgrubinger/pen/MYWQRx" --codepen-code

    # Fetch any Cloudflare-protected or SPA page as text
    python3 fetch-page.py "https://uiverse.io/cssbuttons-io/smart-turkey-45"

    # Fetch with a custom CSS selector
    python3 fetch-page.py "https://example.com" --selector "main.content"

    # Wait longer for slow pages
    python3 fetch-page.py "https://example.com" --wait 20

Outputs page text content to stdout. Use --codepen-code to extract
structured HTML/CSS/JS JSON from CodePen pens.
"""

import argparse
import json
import re
import sys

from playwright.sync_api import sync_playwright


def strip_line_numbers(text):
    """Remove line numbers from CodeMirror editor output.

    CodeMirror renders lines as "1\\ncode line\\n2\\ncode line\\n..."
    This strips the leading line numbers.
    """
    lines = text.split("\n")
    cleaned = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip lines that are just a number (line numbers from CodeMirror)
        if re.match(r"^\d+$", line.strip()):
            i += 1
            continue
        # Also handle zero-width spaces that CodeMirror uses for empty lines
        if line.strip() in ("\u200b", ""):
            cleaned.append("")
        else:
            # Strip non-breaking spaces that CodeMirror uses for indentation
            cleaned.append(line.replace("\xa0", " "))
        i += 1
    # Remove trailing empty lines
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned)


def fetch_codepen_code(page):
    """Extract HTML, CSS, and JS code from a CodePen pen page."""
    result = {}

    # Read from CodeMirror / code editor elements
    for lang, selectors in {
        "html": ["#box-html .CodeMirror", ".html-editor", "[data-lang='html']"],
        "css": ["#box-css .CodeMirror", ".css-editor", "[data-lang='css']"],
        "js": ["#box-js .CodeMirror", ".js-editor", "[data-lang='js']"],
    }.items():
        for sel in selectors:
            try:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text:
                        cleaned = strip_line_numbers(text)
                        if cleaned:
                            result[lang] = cleaned
                        break
            except Exception:
                pass

    return result


def navigate_and_wait(page, url, wait):
    """Navigate to URL and wait for Cloudflare challenge to resolve."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=wait * 1000)
        page.wait_for_load_state("networkidle", timeout=wait * 1000)

        # Extra wait if still on Cloudflare challenge page
        if "Just a moment" in (page.title() or ""):
            page.wait_for_function(
                "document.title !== 'Just a moment...'",
                timeout=wait * 1000,
            )
            page.wait_for_load_state("networkidle", timeout=wait * 1000)

    except Exception as e:
        print(f"Warning: page load timeout/error: {e}", file=sys.stderr)


def fetch_page(url, selector=None, wait=15, codepen_code=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) "
                "Gecko/20100101 Firefox/128.0"
            )
        )
        page = context.new_page()

        navigate_and_wait(page, url, wait)

        if codepen_code:
            code = fetch_codepen_code(page)
            if code:
                print(json.dumps(code, indent=2))
            else:
                print("Could not extract code from CodePen pen.", file=sys.stderr)
                # Fall back to full page text
                print(page.inner_text("body")[:3000])
        elif selector:
            elements = page.query_selector_all(selector)
            for el in elements:
                text = el.inner_text().strip()
                if text:
                    print(text)
                    print("---")
        else:
            print(page.inner_text("body"))

        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Fetch page content with Playwright")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--selector", help="CSS selector to extract specific elements")
    parser.add_argument(
        "--wait", type=int, default=15, help="Max wait time in seconds (default: 15)"
    )
    parser.add_argument(
        "--codepen-code",
        action="store_true",
        help="Extract HTML/CSS/JS code from a CodePen pen",
    )
    args = parser.parse_args()
    fetch_page(args.url, args.selector, args.wait, args.codepen_code)


if __name__ == "__main__":
    main()

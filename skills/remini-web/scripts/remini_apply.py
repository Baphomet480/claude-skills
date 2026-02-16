#!/usr/bin/env python3
"""Apply Remini Web enhancements with an interactive Playwright workflow."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:
    print("Playwright is not installed.", file=sys.stderr)
    print("Install with: python3 -m pip install playwright", file=sys.stderr)
    print("Then run: python3 -m playwright install chromium", file=sys.stderr)
    raise SystemExit(2)

DEFAULT_URL = "https://app.remini.ai/"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
DEFAULT_ACTION_LABELS = [
    "Enhance",
    "Generate",
    "Apply",
    "Start",
    "Upscale",
    "Restore",
    "Retouch",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open Remini Web, upload an image, and capture the downloaded result."
    )
    parser.add_argument("image", help="Input image file path")
    parser.add_argument("--url", default=DEFAULT_URL, help="Remini web URL")
    parser.add_argument(
        "--output",
        help="Optional output path. If omitted, keep Remini suggested filename in downloads dir.",
    )
    parser.add_argument(
        "--profile-dir",
        default="~/.cache/remini-web/profile",
        help="Persistent Chromium profile directory",
    )
    parser.add_argument(
        "--downloads-dir",
        default="~/.cache/remini-web/downloads",
        help="Download directory used by Playwright",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Seconds to wait for a download event",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run headless (visible mode is usually easier for manual login)",
    )
    parser.add_argument(
        "--no-auto-upload",
        action="store_false",
        dest="auto_upload",
        help="Skip automatic file-input upload attempts",
    )
    parser.add_argument(
        "--no-auto-start",
        action="store_false",
        dest="auto_start",
        help="Skip automatic action-button click attempts",
    )
    parser.add_argument(
        "--action-label",
        action="append",
        default=[],
        help="Extra action button label to try (repeatable)",
    )
    parser.add_argument(
        "--accept-any-extension",
        action="store_true",
        help="Allow unsupported input suffixes",
    )
    parser.set_defaults(auto_upload=True, auto_start=True)
    return parser.parse_args()


def resolve_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()


def validate_image_path(path: Path, accept_any_extension: bool) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Input path is not a file: {path}")
    if not accept_any_extension and path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"Unsupported input extension '{path.suffix}'. Allowed: {allowed}. "
            "Use --accept-any-extension to override."
        )


def snapshot_directory_files(directory: Path) -> set[Path]:
    if not directory.exists():
        return set()
    return {p.resolve() for p in directory.iterdir() if p.is_file()}


def newest_file_since_snapshot(directory: Path, snapshot: set[Path]) -> Path | None:
    if not directory.exists():
        return None
    candidates = [p for p in directory.iterdir() if p.is_file() and p.resolve() not in snapshot]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def dedupe_labels(labels: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for label in labels:
        key = label.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(label.strip())
    return deduped


def try_upload_via_file_input(page, image_path: Path) -> bool:
    selectors = [
        "input[type='file']",
        "input[accept*='image']",
        "input[data-testid*='upload']",
        "input[name*='upload']",
    ]

    for frame in page.frames:
        for selector in selectors:
            locator = frame.locator(selector)
            try:
                count = locator.count()
            except Exception:
                continue

            for idx in range(min(count, 5)):
                candidate = locator.nth(idx)
                try:
                    candidate.set_input_files(str(image_path), timeout=1500)
                    print(f"[ok] Uploaded with selector {selector} in frame {frame.url}")
                    return True
                except Exception:
                    continue
    return False


def try_click_action_button(page, labels: Iterable[str]) -> bool:
    for frame in page.frames:
        for label in labels:
            pattern = re.compile(re.escape(label), re.IGNORECASE)
            locator = frame.get_by_role("button", name=pattern)
            try:
                if locator.count() == 0:
                    continue
                locator.first.click(timeout=1500)
                print(f"[ok] Clicked action button matching '{label}'")
                return True
            except Exception:
                continue
    return False


def choose_output_path(download_suggested_filename: str, downloads_dir: Path, output: Path | None) -> Path:
    if output is None:
        destination = downloads_dir / download_suggested_filename
    else:
        destination = output
        if not destination.suffix:
            suggested_suffix = Path(download_suggested_filename).suffix
            if suggested_suffix:
                destination = destination.with_suffix(suggested_suffix)
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def run() -> int:
    args = parse_args()

    image_path = resolve_path(args.image)
    output_path = resolve_path(args.output) if args.output else None
    profile_dir = resolve_path(args.profile_dir)
    downloads_dir = resolve_path(args.downloads_dir)

    validate_image_path(image_path, accept_any_extension=args.accept_any_extension)

    profile_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    before_download_snapshot = snapshot_directory_files(downloads_dir)

    labels = dedupe_labels([*DEFAULT_ACTION_LABELS, *args.action_label])

    print(f"[info] Opening Remini at {args.url}")
    print(f"[info] Browser profile: {profile_dir}")
    print(f"[info] Downloads directory: {downloads_dir}")

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=args.headless,
            accept_downloads=True,
            downloads_path=str(downloads_dir),
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(args.url, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)

            print("[info] Log in manually if needed, then continue in the opened browser.")

            if args.auto_upload:
                if not try_upload_via_file_input(page, image_path):
                    print("[warn] Could not auto-upload image. Upload manually in browser.")
            else:
                print("[info] Auto-upload disabled. Upload manually in browser.")

            if args.auto_start:
                if not try_click_action_button(page, labels):
                    print("[warn] Could not auto-click action button. Start enhancement manually.")
            else:
                print("[info] Auto-start disabled. Start enhancement manually in browser.")

            print("[info] After processing completes, click Remini's Download button.")
            print(f"[info] Waiting up to {args.timeout} seconds for download...")

            try:
                download = context.wait_for_event("download", timeout=max(args.timeout, 1) * 1000)
                destination = choose_output_path(download.suggested_filename, downloads_dir, output_path)
                download.save_as(str(destination))
                print(f"[ok] Saved output: {destination}")
                return 0
            except PlaywrightTimeoutError:
                newest = newest_file_since_snapshot(downloads_dir, before_download_snapshot)
                if newest is None:
                    print("[error] Timed out waiting for download and found no new file.", file=sys.stderr)
                    return 1

                if output_path and newest.resolve() != output_path.resolve():
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(newest, output_path)
                    print(f"[ok] Found new file {newest} and copied to {output_path}")
                    return 0

                print(f"[ok] Found new download file: {newest}")
                return 0
        finally:
            context.close()


def main() -> None:
    try:
        raise SystemExit(run())
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        raise SystemExit(130)


if __name__ == "__main__":
    main()

# Remini Web Workflow Reference

## Defaults

- Default URL: `https://app.remini.ai/`
- Default browser profile: `~/.cache/remini-web/profile`
- Default download directory: `~/.cache/remini-web/downloads`
- Default timeout: `600` seconds

## Automation Strategy

The helper script intentionally uses a mixed mode:

1. Keep account authentication manual.
2. Attempt predictable automation for upload/action buttons.
3. Fall back to manual UI actions when selectors shift.
4. Capture the generated file through Playwright download events.

This keeps the flow resilient when Remini UI text changes.

## Upload Matching

The script probes file inputs in this order:

- `input[type="file"]`
- `input[accept*="image"]`
- `input[data-testid*="upload"]`
- `input[name*="upload"]`

If no input is found, upload manually in the browser and continue.

## Action Button Matching

Default button labels:

- `Enhance`
- `Generate`
- `Apply`
- `Start`
- `Upscale`
- `Restore`
- `Retouch`

Add extra labels with repeated `--action-label` flags.

## Troubleshooting

### Playwright is missing

Install dependencies:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

### Script cannot find upload input

- Use manual upload in browser.
- Re-run with `--no-auto-upload` to skip upload probing.

### Script clicks the wrong button

- Re-run with `--no-auto-start`.
- Start enhancement manually.

### Script times out waiting for download

- Increase timeout with `--timeout 900`.
- Confirm you clicked Remini's final Download button.
- Check the download directory directly for produced files.

### Session expires often

- Keep the same `--profile-dir` between runs.
- Log in once with visible browser mode (default).

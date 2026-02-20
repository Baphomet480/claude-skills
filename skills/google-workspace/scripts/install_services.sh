#!/bin/bash
# Install Google Workspace systemd services with correct paths.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
SYSTEMD_DIR="$HOME/.config/systemd/user"

# Detect uv path
UV_PATH=$(which uv || echo "/usr/bin/uv")
if [[ ! -x "$UV_PATH" ]]; then
    echo "Error: 'uv' not found in PATH. Please install uv first."
    exit 1
fi

echo "Installing services to $SYSTEMD_DIR..."
mkdir -p "$SYSTEMD_DIR"

# Template replacement
svc="workspace-token-maintainer"
echo "  Configuring $svc.service..."
sed -e "s|%INSTALL_DIR%|$SKILL_ROOT|g" \
    -e "s|%UV_PATH%|$UV_PATH|g" \
    "$SCRIPT_DIR/$svc.service.template" > "$SYSTEMD_DIR/$svc.service"

if [[ -f "$SCRIPT_DIR/$svc.timer" ]]; then
    echo "  Installing $svc.timer..."
    cp "$SCRIPT_DIR/$svc.timer" "$SYSTEMD_DIR/"
else
    echo "Warning: $svc.timer not found!"
fi

systemctl --user daemon-reload
echo "Done."
echo
echo "To enable token maintenance:"
echo "  systemctl --user enable --now workspace-token-maintainer.timer"

#!/bin/bash
# Removes everything install.sh created for the current user.
set -u

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}"
BIN_DIR="$HOME/.local/bin"
APP_DATA_DIR="$DATA_DIR/kaislideshow"

rm -rf "$APP_DATA_DIR"
rm -f "$BIN_DIR/kaislideshow"
rm -f "$DATA_DIR/applications/kaislideshow.desktop"
rm -f "$DATA_DIR/icons/hicolor/scalable/apps/kaislideshow.svg"
rm -f "$DATA_DIR/nemo/actions/kaislideshow.nemo_action"
rm -f "$DATA_DIR/nautilus/scripts/Start KaiSlideshow"

# COSMIC Files' context_actions is one shared file, not one file per app,
# so only remove it if it's exactly what install.sh generated - otherwise
# it either holds the user's own other actions, or theirs merged with ours.
COSMIC_CONFIG_BASE="${XDG_CONFIG_HOME:-$HOME/.config}"
COSMIC_ACTIONS_FILE="$COSMIC_CONFIG_BASE/cosmic/com.system76.CosmicFiles/v1/context_actions"
if [ -f "$COSMIC_ACTIONS_FILE" ]; then
    if diff -q "$REPO_DIR/packaging/cosmic-files/context_actions" "$COSMIC_ACTIONS_FILE" >/dev/null 2>&1; then
        rm -f "$COSMIC_ACTIONS_FILE"
    elif grep -q "KaiSlideshow" "$COSMIC_ACTIONS_FILE" 2>/dev/null; then
        echo "Note: $COSMIC_ACTIONS_FILE has other custom actions besides KaiSlideshow's, so it was left in place - remove the KaiSlideshow entry from it manually if you want."
    fi
fi

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA_DIR/applications" >/dev/null 2>&1
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$DATA_DIR/icons/hicolor" >/dev/null 2>&1

echo "KaiSlideshow has been uninstalled. The settings file in ~/.config/kaislideshow was kept (delete it manually if you want)."

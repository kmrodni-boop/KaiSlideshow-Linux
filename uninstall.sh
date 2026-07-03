#!/bin/bash
# Removes everything install.sh created for the current user.
set -u

DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}"
BIN_DIR="$HOME/.local/bin"
APP_DATA_DIR="$DATA_DIR/kaislideshow"

rm -rf "$APP_DATA_DIR"
rm -f "$BIN_DIR/kaislideshow"
rm -f "$DATA_DIR/applications/kaislideshow.desktop"
rm -f "$DATA_DIR/icons/hicolor/scalable/apps/kaislideshow.svg"
rm -f "$DATA_DIR/nemo/actions/kaislideshow.nemo_action"
rm -f "$DATA_DIR/nautilus/scripts/Start KaiSlideshow"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA_DIR/applications" >/dev/null 2>&1
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$DATA_DIR/icons/hicolor" >/dev/null 2>&1

echo "KaiSlideshow er avinstallert. Innstillingsfilen i ~/.config/kaislideshow er beholdt (slett manuelt om onskelig)."

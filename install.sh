#!/bin/bash
# Installs KaiSlideshow for the current user:
#   - creates an isolated Python venv and installs PySide6 into it
#   - installs a `kaislideshow` launcher on your PATH (~/.local/bin)
#   - installs the .desktop entry + icon so the app shows up in file
#     managers' "Open with" menus (Nemo, GNOME Files/Nautilus, COSMIC
#     Files, Dolphin, Thunar, ...)
#   - installs a dedicated "Start KaiSlideshow" right-click action for
#     Nemo, and a right-click "Scripts" entry for Nautilus
#
# Nothing is installed system-wide and no files outside $HOME are touched.
set -u

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}"
BIN_DIR="$HOME/.local/bin"
APP_DATA_DIR="$DATA_DIR/kaislideshow"
VENV_DIR="$APP_DATA_DIR/venv"
ASSUME_YES=0

for arg in "$@"; do
    case "$arg" in
        -y|--yes) ASSUME_YES=1 ;;
        -h|--help)
            echo "Usage: $0 [-y|--yes]"
            echo "  -y, --yes   Don't prompt before installing missing system packages."
            exit 0
            ;;
    esac
done

confirm() {
    [ "$ASSUME_YES" = "1" ] && return 0
    read -r -p "$1 [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]]
}

echo "== KaiSlideshow installer =="

# ---------------------------------------------------------------- python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 was not found. Install Python 3.9+ and run this script again." >&2
    exit 1
fi

# ---------------------------------------------------------- venv module
if ! python3 -c "import venv" >/dev/null 2>&1; then
    echo "The Python 'venv' module is missing."
    PKG=""
    if command -v apt >/dev/null 2>&1; then PKG="sudo apt install -y python3-venv python3-pip"
    elif command -v dnf >/dev/null 2>&1; then PKG="sudo dnf install -y python3-venv python3-pip"
    elif command -v pacman >/dev/null 2>&1; then PKG="sudo pacman -S --needed python-virtualenv python-pip"
    elif command -v zypper >/dev/null 2>&1; then PKG="sudo zypper install -y python3-venv python3-pip"
    fi
    if [ -n "$PKG" ]; then
        echo "Suggested command: $PKG"
        if confirm "Run this command now?"; then
            eval "$PKG"
        else
            echo "Skipping. Install it manually and run this script again." >&2
            exit 1
        fi
    else
        echo "No known package manager found. Install python3-venv manually." >&2
        exit 1
    fi
fi

# --------------------------------------------------------------- venv + deps
echo "Creating/updating the virtual environment in $VENV_DIR ..."
mkdir -p "$APP_DATA_DIR"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip wheel >/dev/null
echo "Installing KaiSlideshow and its dependencies (PySide6) ..."
"$VENV_DIR/bin/pip" install --upgrade "$REPO_DIR"
# pip sees that "kaislideshow" is already at the same version number and
# skips reinstalling it, even if the source code has changed. Force a
# fresh install of the package itself (without touching PySide6).
"$VENV_DIR/bin/pip" install --upgrade --force-reinstall --no-deps "$REPO_DIR"

# --------------------------------------------------------------- launcher
mkdir -p "$BIN_DIR"
LAUNCHER="$BIN_DIR/kaislideshow"
cat > "$LAUNCHER" <<EOF
#!/bin/bash
exec "$VENV_DIR/bin/python" -m kaislideshow "\$@"
EOF
chmod +x "$LAUNCHER"
echo "Installed command: $LAUNCHER"

# --------------------------------------------------------------- .desktop + icon
mkdir -p "$DATA_DIR/applications" "$DATA_DIR/icons/hicolor/scalable/apps"
cp "$REPO_DIR/packaging/kaislideshow.desktop" "$DATA_DIR/applications/kaislideshow.desktop"
cp "$REPO_DIR/packaging/icons/kaislideshow.svg" "$DATA_DIR/icons/hicolor/scalable/apps/kaislideshow.svg"
echo "Installed the .desktop entry and icon."

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA_DIR/applications" >/dev/null 2>&1
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$DATA_DIR/icons/hicolor" >/dev/null 2>&1

# --------------------------------------------------------------- Nemo action
mkdir -p "$DATA_DIR/nemo/actions"
cp "$REPO_DIR/packaging/nemo-actions/kaislideshow.nemo_action" "$DATA_DIR/nemo/actions/kaislideshow.nemo_action"
if command -v nemo >/dev/null 2>&1; then
    echo "Installed the Nemo action: right-click images/folders -> 'Start KaiSlideshow'."
else
    echo "Installed the Nemo action (Nemo wasn't found now, but the action will be picked up if you install Nemo later)."
fi

# --------------------------------------------------------------- Nautilus script
mkdir -p "$DATA_DIR/nautilus/scripts"
cp "$REPO_DIR/packaging/nautilus-scripts/Start KaiSlideshow" "$DATA_DIR/nautilus/scripts/Start KaiSlideshow"
chmod +x "$DATA_DIR/nautilus/scripts/Start KaiSlideshow"
if command -v nautilus >/dev/null 2>&1; then
    echo "Installed the Nautilus script: right-click -> Scripts -> 'Start KaiSlideshow'."
fi

# --------------------------------------------------------------- COSMIC Files note
if command -v cosmic-files >/dev/null 2>&1; then
    echo
    echo "Note about COSMIC Files: it doesn't yet support custom right-click"
    echo "actions (see pop-os/cosmic-files#1445), so KaiSlideshow will show up"
    echo "under right-click -> 'Open With' -> KaiSlideshow instead of as its"
    echo "own menu entry. It's there because the .desktop file above"
    echo "registers KaiSlideshow as a valid opener for images/folders."
fi

# --------------------------------------------------------------- PATH check
case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        echo
        echo "NOTE: $BIN_DIR is not in your PATH."
        RC_FILE="$HOME/.bashrc"
        [ -n "${ZSH_VERSION:-}" ] && RC_FILE="$HOME/.zshrc"
        LINE='export PATH="$HOME/.local/bin:$PATH"'
        if confirm "Add '$LINE' to $RC_FILE?"; then
            echo "$LINE" >> "$RC_FILE"
            echo "Added. Open a new terminal (or log in again) for it to take effect."
        else
            echo "Add it manually: $LINE"
        fi
        ;;
esac

echo
echo "== Done! =="
echo "Start with:           kaislideshow"
echo "Or right-click images/folders in your file manager and choose KaiSlideshow."

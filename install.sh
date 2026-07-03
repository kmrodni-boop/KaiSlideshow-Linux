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
    echo "python3 ble ikke funnet. Installer Python 3.9+ og kjor dette skriptet på nytt." >&2
    exit 1
fi

# ---------------------------------------------------------- venv module
if ! python3 -c "import venv" >/dev/null 2>&1; then
    echo "Python-modulen 'venv' mangler."
    PKG=""
    if command -v apt >/dev/null 2>&1; then PKG="sudo apt install -y python3-venv python3-pip"
    elif command -v dnf >/dev/null 2>&1; then PKG="sudo dnf install -y python3-venv python3-pip"
    elif command -v pacman >/dev/null 2>&1; then PKG="sudo pacman -S --needed python-virtualenv python-pip"
    elif command -v zypper >/dev/null 2>&1; then PKG="sudo zypper install -y python3-venv python3-pip"
    fi
    if [ -n "$PKG" ]; then
        echo "Foreslatt kommando: $PKG"
        if confirm "Kjore denne kommandoen na?"; then
            eval "$PKG"
        else
            echo "Hopper over. Installer manuelt og kjor dette skriptet på nytt." >&2
            exit 1
        fi
    else
        echo "Fant ingen kjent pakkebehandler. Installer python3-venv manuelt." >&2
        exit 1
    fi
fi

# --------------------------------------------------------------- venv + deps
echo "Oppretter/oppdaterer virtuelt miljo i $VENV_DIR ..."
mkdir -p "$APP_DATA_DIR"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip wheel >/dev/null
echo "Installerer KaiSlideshow og avhengigheter (PySide6) ..."
"$VENV_DIR/bin/pip" install --upgrade "$REPO_DIR"

# --------------------------------------------------------------- launcher
mkdir -p "$BIN_DIR"
LAUNCHER="$BIN_DIR/kaislideshow"
cat > "$LAUNCHER" <<EOF
#!/bin/bash
exec "$VENV_DIR/bin/python" -m kaislideshow "\$@"
EOF
chmod +x "$LAUNCHER"
echo "Installerte kommando: $LAUNCHER"

# --------------------------------------------------------------- .desktop + icon
mkdir -p "$DATA_DIR/applications" "$DATA_DIR/icons/hicolor/scalable/apps"
cp "$REPO_DIR/packaging/kaislideshow.desktop" "$DATA_DIR/applications/kaislideshow.desktop"
cp "$REPO_DIR/packaging/icons/kaislideshow.svg" "$DATA_DIR/icons/hicolor/scalable/apps/kaislideshow.svg"
echo "Installerte .desktop-oppforing og ikon."

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA_DIR/applications" >/dev/null 2>&1
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$DATA_DIR/icons/hicolor" >/dev/null 2>&1

# --------------------------------------------------------------- Nemo action
mkdir -p "$DATA_DIR/nemo/actions"
cp "$REPO_DIR/packaging/nemo-actions/kaislideshow.nemo_action" "$DATA_DIR/nemo/actions/kaislideshow.nemo_action"
if command -v nemo >/dev/null 2>&1; then
    echo "Installerte Nemo-handling: hoyreklikk pa bilder/mapper -> 'Start KaiSlideshow'."
else
    echo "Installerte Nemo-handling (Nemo ble ikke funnet na, men handlingen tas i bruk hvis du installerer Nemo senere)."
fi

# --------------------------------------------------------------- Nautilus script
mkdir -p "$DATA_DIR/nautilus/scripts"
cp "$REPO_DIR/packaging/nautilus-scripts/Start KaiSlideshow" "$DATA_DIR/nautilus/scripts/Start KaiSlideshow"
chmod +x "$DATA_DIR/nautilus/scripts/Start KaiSlideshow"
if command -v nautilus >/dev/null 2>&1; then
    echo "Installerte Nautilus-skript: hoyreklikk -> Scripts -> 'Start KaiSlideshow'."
fi

# --------------------------------------------------------------- COSMIC Files note
if command -v cosmic-files >/dev/null 2>&1; then
    echo
    echo "Merk om COSMIC Files: den stotter foreløpig ikke egendefinerte"
    echo "hoyreklikk-handlinger (se pop-os/cosmic-files#1445), sa KaiSlideshow"
    echo "vil vise seg under hoyreklikk -> 'Apne med' -> KaiSlideshow i stedet"
    echo "for som en egen menylinje. Den finnes fordi .desktop-filen over"
    echo "registrerer KaiSlideshow som en gyldig apner for bilder/mapper."
fi

# --------------------------------------------------------------- PATH check
case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        echo
        echo "OBS: $BIN_DIR er ikke i din PATH."
        RC_FILE="$HOME/.bashrc"
        [ -n "${ZSH_VERSION:-}" ] && RC_FILE="$HOME/.zshrc"
        LINE='export PATH="$HOME/.local/bin:$PATH"'
        if confirm "Legge til '$LINE' i $RC_FILE?"; then
            echo "$LINE" >> "$RC_FILE"
            echo "Lagt til. Start en ny terminal (eller logg inn pa nytt) for at det skal tre i kraft."
        else
            echo "Legg til manuelt: $LINE"
        fi
        ;;
esac

echo
echo "== Ferdig! =="
echo "Start med:            kaislideshow"
echo "Eller hoyreklikk pa bilder/mapper i filbehandleren din og velg KaiSlideshow."

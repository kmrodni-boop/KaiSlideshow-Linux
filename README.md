# KaiSlideshow-Linux

A lightweight fullscreen image slideshow viewer for Linux, written in Python with PySide6 (Qt6).
Sister app to [KaiSlideshow-Android](https://github.com/kmrodni-boop/KaiSlideshow-Android),
built with the same philosophy: do one thing well — show your photos as a
slideshow, without unnecessary complexity.

## Features

- **Fullscreen slideshow** with configurable interval (2–120 sec)
- **Shuffle or alphabetical** order
- **Fade transitions** between images, can be toggled on/off
- **Sleep timer** that ends the slideshow after a chosen time
- **Zoom and pan** with the mouse wheel/click-and-drag while paused
- **EXIF-aware rotation** — photos from phones/cameras display the right way up
- **Background scanning** — large folders load without freezing the UI
- **Add more images/folders** on the fly, without restarting
- **Recent folders** remembered between sessions
- **Info bar** showing image number and filename
- Resilient to unreadable/corrupt files — they're skipped automatically

### Keyboard and mouse

| Action | Effect |
|---|---|
| `Space` | Pause / resume |
| `→` / `Enter` | Next image |
| `←` | Previous image |
| `Esc` | Quit |
| `F` / `F11` | Toggle fullscreen |
| Mouse wheel (paused) | Zoom in/out |
| Click + drag (paused, zoomed) | Pan |
| `+` / `-` / `0` (paused) | Zoom in / out / reset |
| Move mouse | Show control bar and cursor |

The control bar at the top (shown when you move the mouse) has the interval,
shuffle, fade, sleep timer, previous/next, "Add images", "Add folders" and "Quit".

## Installation

```bash
git clone https://github.com/kmrodni-boop/KaiSlideshow-Linux.git
cd KaiSlideshow-Linux
bash install.sh
```

(If the script is executable on your system you can also run `./install.sh`
directly; run `chmod +x install.sh uninstall.sh` first if needed.)

`install.sh` does the following, for your user account only (nothing is
installed system-wide, no files outside `$HOME` are touched):

1. Checks that `python3` and the `venv` module are available. If missing,
   it suggests the right package for your distro (apt/dnf/pacman/zypper)
   and asks before installing anything.
2. Creates an isolated virtual environment in
   `~/.local/share/kaislideshow/venv` and installs `PySide6` and the app
   there — your system Python is untouched.
3. Adds a `kaislideshow` command to `~/.local/bin` (and offers to add it
   to `PATH` if it's missing).
4. Installs the `.desktop` entry and icon so KaiSlideshow shows up in the
   application menu and in the "Open with" menu for images/folders in all
   XDG-compliant file managers (Nautilus/GNOME Files, Dolphin, Thunar,
   PCManFM, COSMIC Files, ...).
5. Installs a **dedicated "Start KaiSlideshow" action for Nemo** that
   appears directly in the right-click menu for one or more selected
   images/folders — not tucked away under "Open with".
6. Installs a right-click script for Nautilus (GNOME Files) under the
   Scripts submenu.

Run `bash install.sh -y` to answer yes to all prompts automatically
(useful for scripts/CI).

Remove everything again with:

```bash
bash uninstall.sh
```

## Right-click integration per file manager

| File manager | How it shows up |
|---|---|
| **Nemo** (Cinnamon/Linux Mint) | Dedicated **"Start KaiSlideshow"** entry directly in the right-click menu, for one or more selected images/folders |
| **Nautilus** (GNOME Files) | Right-click → **Scripts** → "Start KaiSlideshow" |
| **COSMIC Files** | Right-click → **Open With** → KaiSlideshow. COSMIC Files doesn't yet support custom right-click actions the way Nemo does ([pop-os/cosmic-files#1445](https://github.com/pop-os/cosmic-files/issues/1445) is still open); once that feature lands upstream, a dedicated script can be added here the same way as for Nautilus |
| Dolphin, Thunar, PCManFM, etc. | Right-click → **Open With** → KaiSlideshow (via standard `.desktop` registration) |

In every case you can select **multiple images and/or folders at once** —
KaiSlideshow merges them into a single slideshow.

## Manual usage

```bash
kaislideshow                          # prompts you to pick folders
kaislideshow ~/Pictures/Summer2025    # start directly with a folder
kaislideshow photo1.jpg photo2.png ~/Pictures/Trip  # mix of files and folders
```

## Settings

Stored in `~/.config/kaislideshow/settings.json` (interval, shuffle, fade,
sleep timer, recent folders). Automatically migrated from the old
`~/.slideshow_settings.json` location used by the original prototype, if present.

## Project structure

```
KaiSlideshow-Linux/
├── kaislideshow/
│   ├── __main__.py     # Entry point / argument handling
│   ├── window.py        # Main window: slideshow, UI, zoom/pan, fade
│   ├── loader.py         # Background thread that scans folders/files
│   ├── settings.py       # Settings (XDG config, recent folders)
│   └── constants.py      # Shared constants
├── packaging/
│   ├── kaislideshow.desktop
│   ├── icons/kaislideshow.svg
│   ├── nemo-actions/kaislideshow.nemo_action
│   └── nautilus-scripts/Start KaiSlideshow
├── install.sh / uninstall.sh
├── pyproject.toml
└── requirements.txt
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m kaislideshow
```

## Dependencies

- Python 3.9+
- [PySide6](https://pypi.org/project/PySide6/) (Qt6 bindings)

## License

GNU General Public License v3.0 (GPLv3) — see [LICENSE](LICENSE). Anyone who
redistributes this app or a modified version of it must also make that
version's source available under GPLv3.

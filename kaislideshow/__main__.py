"""Entry point: `kaislideshow [image_or_folder ...]`.

Invoked with no arguments it asks the user to pick images/folders.
Invoked with paths (e.g. from a file manager's "Open with" / right-click
action) it starts the slideshow directly with those files and/or folders.
"""

import sys

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from .constants import APP_NAME, DESKTOP_ID, ORG_NAME
from .window import Slideshow


def _apply_dark_palette(app):
    """Force a consistent dark palette so system dialogs (file pickers,
    message boxes) stay readable regardless of the desktop's GTK/Qt theme
    integration, which is often incomplete for a pip-installed PySide6 on
    Linux and can otherwise render dark-on-dark or black-on-black text."""
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(35, 35, 35))
    palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
    palette.setColor(QPalette.Base, QColor(20, 20, 20))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, QColor(230, 230, 230))
    palette.setColor(QPalette.ToolTipText, QColor(230, 230, 230))
    palette.setColor(QPalette.Text, QColor(230, 230, 230))
    palette.setColor(QPalette.Button, QColor(60, 60, 60))
    palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    palette.setColor(QPalette.BrightText, QColor(255, 80, 80))
    palette.setColor(QPalette.Link, QColor(90, 160, 220))
    palette.setColor(QPalette.Highlight, QColor(51, 130, 200))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 120, 120))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    _apply_dark_palette(app)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setDesktopFileName(DESKTOP_ID)

    # Strip surrounding quotes some file managers add when passing paths.
    args = [p.strip('"') for p in sys.argv[1:]] if len(sys.argv) > 1 else None

    try:
        window = Slideshow(args)
    except SystemExit:
        return 0

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

"""Entry point: `kaislideshow [image_or_folder ...]`.

Invoked with no arguments it asks the user to pick images/folders.
Invoked with paths (e.g. from a file manager's "Open with" / right-click
action) it starts the slideshow directly with those files and/or folders.
"""

import sys

from PySide6.QtWidgets import QApplication

from .constants import APP_NAME, DESKTOP_ID, ORG_NAME
from .window import Slideshow


def main():
    app = QApplication(sys.argv)
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

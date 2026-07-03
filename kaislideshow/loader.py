"""Background scanning of folders/files so large libraries don't freeze the UI."""

import os

from PySide6.QtCore import QThread, Signal

from .constants import IMAGE_EXTENSIONS


class ImageScanner(QThread):
    """Walks the given paths (files and/or directories) off the UI thread."""

    finished_scanning = Signal(list)

    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.paths = paths

    def run(self):
        found = []
        seen = set()
        for path in self.paths:
            if self.isInterruptionRequested():
                break
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    if self.isInterruptionRequested():
                        break
                    dirs.sort()
                    for file in sorted(files):
                        if file.lower().endswith(IMAGE_EXTENSIONS):
                            full = os.path.join(root, file)
                            if full not in seen:
                                seen.add(full)
                                found.append(full)
            elif os.path.isfile(path):
                if path.lower().endswith(IMAGE_EXTENSIONS) and path not in seen:
                    seen.add(path)
                    found.append(path)
        self.finished_scanning.emit(found)

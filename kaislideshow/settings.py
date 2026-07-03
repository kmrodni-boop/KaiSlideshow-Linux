"""Persisted user settings for KaiSlideshow (XDG-compliant config location)."""

import json
import os

from .constants import DEFAULT_SETTINGS, MAX_RECENT_FOLDERS

CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "kaislideshow",
)
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Old location used by the original single-file prototype; migrated on first run.
LEGACY_SETTINGS_FILE = os.path.expanduser("~/.slideshow_settings.json")


class Settings:
    def __init__(self):
        self.data = dict(DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        source = SETTINGS_FILE if os.path.exists(SETTINGS_FILE) else LEGACY_SETTINGS_FILE
        if os.path.exists(source):
            try:
                with open(source, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                self.data.update(loaded)
            except (OSError, json.JSONDecodeError):
                pass

    def save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
        except OSError:
            pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add_recent_folders(self, paths):
        recent = self.data.get("recent_folders", [])
        for path in paths:
            path = os.path.abspath(path)
            if path in recent:
                recent.remove(path)
            recent.insert(0, path)
        self.data["recent_folders"] = recent[:MAX_RECENT_FOLDERS]
        self.save()

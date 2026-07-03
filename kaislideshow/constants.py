"""Shared constants for KaiSlideshow."""

APP_NAME = "KaiSlideshow"
ORG_NAME = "kmrodni"
DESKTOP_ID = "com.kmrodni.kaislideshow"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff")

INTERVAL_CHOICES = ["2", "3", "5", "10", "20", "30", "60", "120"]

SLEEP_TIMER_CHOICES = {
    "Av": 0,
    "15 min": 15,
    "30 min": 30,
    "1 time": 60,
    "2 timer": 120,
    "4 timer": 240,
}

MAX_RECENT_FOLDERS = 10

DEFAULT_SETTINGS = {
    "interval": "5",
    "shuffle": True,
    "fade": True,
    "sleep_timer": "Av",
    "recent_folders": [],
}

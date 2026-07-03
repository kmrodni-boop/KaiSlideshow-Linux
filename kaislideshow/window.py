"""Main slideshow window."""

import os
import random

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QImageReader, QKeyEvent, QMouseEvent, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QListView,
    QMainWindow,
    QPushButton,
)

from .constants import DONATE_URL, INTERVAL_CHOICES, SLEEP_TIMER_CHOICES
from .loader import ImageScanner
from .settings import Settings

MIN_ZOOM = 1.0
MAX_ZOOM = 4.0
ZOOM_STEP = 0.15
FADE_MS = 180


def load_pixmap(path):
    """Load an image respecting EXIF orientation (phone photos etc.)."""
    reader = QImageReader(path)
    reader.setAutoTransform(True)
    image = reader.read()
    if image.isNull():
        return QPixmap()
    return QPixmap.fromImage(image)


class Slideshow(QMainWindow):
    def __init__(self, paths=None):
        super().__init__()
        self.setWindowTitle("KaiSlideshow")
        self.setStyleSheet("background-color: black;")
        self.setMouseTracking(True)

        self.settings = Settings()
        self.image_list = []
        self.index = 0
        self.scanner = None

        self.raw_pixmap = QPixmap()
        self.zoom = MIN_ZOOM
        self.pan = QPoint(0, 0)
        self.drag_origin = None
        self.drag_pan_origin = None

        if not paths:
            paths = self.select_folder_paths()
        if not paths:
            raise SystemExit(0)

        self._build_ui()
        self._start_scan(paths, initial=True)

        self.showFullScreen()
        self.mouse_timer.start(2000)

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMouseTracking(True)
        self.label.setFocusPolicy(Qt.NoFocus)
        self.opacity_effect = QGraphicsOpacityEffect(self.label)
        self.opacity_effect.setOpacity(1.0)
        self.label.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.setCentralWidget(self.label)

        self.status_label = QLabel("Laster bilder…", self)
        self.status_label.setStyleSheet("color: #ddd; font-size: 22px;")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.info_bar = QLabel(self)
        self.info_bar.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: #ddd; padding: 8px 15px;"
            " border-bottom-right-radius: 12px;"
        )
        self.info_bar.setFocusPolicy(Qt.NoFocus)

        self.pause_label = QLabel("Ⅱ PAUSE", self)
        self.pause_label.setStyleSheet(
            "background-color: rgba(20, 20, 20, 200); color: white; font-size: 50px;"
            " font-weight: bold; border-radius: 25px; padding: 40px; border: 1px solid #444;"
        )
        self.pause_label.setAlignment(Qt.AlignCenter)
        self.pause_label.hide()

        self._build_menu_bar()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next)
        self.timer.start(self._interval_ms())

        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.hide_ui)

        self.sleep_timer = QTimer(self)
        self.sleep_timer.setSingleShot(True)
        self.sleep_timer.timeout.connect(self.close)
        self._apply_sleep_timer(self.settings.get("sleep_timer", "Av"))

    def _build_menu_bar(self):
        self.menu_bar = QFrame(self)
        self.menu_bar.setFixedHeight(80)
        self.menu_bar.setFocusPolicy(Qt.NoFocus)
        self.menu_bar.setStyleSheet(
            """
            QFrame { background-color: rgba(35, 35, 35, 230); border-radius: 20px; border: 1px solid #555; }
            QLabel { color: #eee; font-size: 14px; }
            QComboBox { color: white; background-color: #444; border: 1px solid #666; padding: 5px; border-radius: 8px; }
            QCheckBox { color: white; }
            QPushButton { color: white; background-color: #444; border: none; padding: 8px 16px; border-radius: 10px; font-weight: bold; }
            """
        )
        self.menu_bar.hide()

        layout = QHBoxLayout(self.menu_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Intervall:"))
        self.timer_combo = QComboBox()
        self.timer_combo.addItems(INTERVAL_CHOICES)
        self.timer_combo.setCurrentText(str(self.settings.get("interval", "5")))
        self.timer_combo.setFocusPolicy(Qt.NoFocus)
        self.timer_combo.currentTextChanged.connect(self.update_interval)
        layout.addWidget(self.timer_combo)

        self.shuffle_check = QCheckBox("Tilfeldig")
        self.shuffle_check.setChecked(self.settings.get("shuffle", True))
        self.shuffle_check.setFocusPolicy(Qt.NoFocus)
        self.shuffle_check.stateChanged.connect(self.toggle_shuffle)
        layout.addWidget(self.shuffle_check)

        self.fade_check = QCheckBox("Uttoning")
        self.fade_check.setChecked(self.settings.get("fade", True))
        self.fade_check.setFocusPolicy(Qt.NoFocus)
        self.fade_check.stateChanged.connect(self.toggle_fade)
        layout.addWidget(self.fade_check)

        layout.addWidget(QLabel("Sovetimer:"))
        self.sleep_combo = QComboBox()
        self.sleep_combo.addItems(list(SLEEP_TIMER_CHOICES.keys()))
        self.sleep_combo.setCurrentText(self.settings.get("sleep_timer", "Av"))
        self.sleep_combo.setFocusPolicy(Qt.NoFocus)
        self.sleep_combo.currentTextChanged.connect(self.update_sleep_timer)
        layout.addWidget(self.sleep_combo)

        layout.addStretch()

        self.prev_btn = QPushButton("◀ Forrige")
        self.prev_btn.setFocusPolicy(Qt.NoFocus)
        self.prev_btn.clicked.connect(self.show_previous)
        layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Neste ▶")
        self.next_btn.setFocusPolicy(Qt.NoFocus)
        self.next_btn.clicked.connect(self.show_next)
        layout.addWidget(self.next_btn)

        self.add_files_btn = QPushButton("Legg til bilder")
        self.add_files_btn.setStyleSheet("background-color: #2980b9; color: white;")
        self.add_files_btn.setFocusPolicy(Qt.NoFocus)
        self.add_files_btn.clicked.connect(self.add_more_files)
        layout.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton("Legg til mapper")
        self.add_folder_btn.setStyleSheet("background-color: #2980b9; color: white;")
        self.add_folder_btn.setFocusPolicy(Qt.NoFocus)
        self.add_folder_btn.clicked.connect(self.add_more_folders)
        layout.addWidget(self.add_folder_btn)

        self.donate_btn = QPushButton("♡ Doner")
        self.donate_btn.setToolTip("Stott utviklingen av KaiSlideshow")
        self.donate_btn.setFocusPolicy(Qt.NoFocus)
        self.donate_btn.clicked.connect(self.open_donate_link)
        layout.addWidget(self.donate_btn)

        self.close_btn = QPushButton("Avslutt")
        self.close_btn.setStyleSheet("background-color: #c0392b; color: white;")
        self.close_btn.setFocusPolicy(Qt.NoFocus)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

    # ------------------------------------------------------------- dialogs

    def select_folder_paths(self):
        """Ask the user for one or more folders. Native dialogs rarely allow
        picking several folders at once, so this uses a non-native dialog with
        multi-selection enabled (works on most Linux desktops)."""
        dialog = QFileDialog(self, "Velg mapper")
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        for view in dialog.findChildren(QListView):
            view.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        if dialog.exec():
            return dialog.selectedFiles()
        return None

    # --------------------------------------------------------- image scan

    def _start_scan(self, paths, initial=False):
        if self.scanner is not None and self.scanner.isRunning():
            self.scanner.requestInterruption()
            self.scanner.wait()

        self.status_label.show()
        self.status_label.raise_()
        self._center_status_label()

        self.scanner = ImageScanner(paths)
        self.scanner.finished_scanning.connect(
            lambda found: self._on_scan_finished(found, replace=initial)
        )
        self.scanner.start()

        folders = [p for p in paths if os.path.isdir(p)]
        if folders:
            self.settings.add_recent_folders(folders)

    def _on_scan_finished(self, found, replace):
        self.status_label.hide()
        if replace:
            self.image_list = found
        else:
            existing = set(self.image_list)
            self.image_list.extend(p for p in found if p not in existing)

        if not self.image_list:
            self.status_label.setText("Ingen bilder funnet i valgte mapper/filer.")
            self.status_label.show()
            return

        self.apply_sorting()
        self.show_next()

    # --------------------------------------------------------------- misc

    def add_more_folders(self):
        new_paths = self.select_folder_paths()
        if new_paths:
            self._start_scan(new_paths, initial=False)

    def add_more_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Legg til bilder")
        if files:
            self._start_scan(files, initial=False)

    def open_donate_link(self):
        QDesktopServices.openUrl(QUrl(DONATE_URL))

    def apply_sorting(self):
        current = self.image_list[self.index] if self.image_list and self.index < len(self.image_list) else None
        if self.settings.get("shuffle", True):
            random.shuffle(self.image_list)
        else:
            self.image_list.sort()
        self.index = self.image_list.index(current) if current in self.image_list else 0

    def hide_ui(self):
        self.menu_bar.hide()
        self.setCursor(Qt.BlankCursor)

    def _interval_ms(self):
        return int(self.timer_combo.currentText()) * 1000

    def _apply_sleep_timer(self, label):
        minutes = SLEEP_TIMER_CHOICES.get(label, 0)
        self.sleep_timer.stop()
        if minutes > 0:
            self.sleep_timer.start(minutes * 60 * 1000)

    def _center_status_label(self):
        self.status_label.adjustSize()
        self.status_label.move(
            (self.width() - self.status_label.width()) // 2,
            (self.height() - self.status_label.height()) // 2,
        )

    # ------------------------------------------------------------- layout

    def resizeEvent(self, event):
        if hasattr(self, "menu_bar"):
            menu_width = min(900, int(self.width() * 0.92))
            self.menu_bar.setFixedWidth(menu_width)
            self.menu_bar.move((self.width() - menu_width) // 2, 40)
        if hasattr(self, "pause_label"):
            self.pause_label.adjustSize()
            self.pause_label.move(
                (self.width() - self.pause_label.width()) // 2,
                (self.height() - self.pause_label.height()) // 2,
            )
        if hasattr(self, "status_label"):
            self._center_status_label()
        if hasattr(self, "label") and not self.raw_pixmap.isNull():
            self._render_frame()
        super().resizeEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.setCursor(Qt.ArrowCursor)
        if hasattr(self, "menu_bar"):
            self.menu_bar.raise_()
            self.menu_bar.show()
            if self.timer.isActive():
                self.mouse_timer.start(3000)

        if self.drag_origin is not None and event.buttons() & Qt.LeftButton and self.zoom > MIN_ZOOM:
            delta = event.position().toPoint() - self.drag_origin
            self.pan = self.drag_pan_origin - delta
            self._render_frame()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.zoom > MIN_ZOOM and not self.timer.isActive():
            self.drag_origin = event.position().toPoint()
            self.drag_pan_origin = self.pan
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_origin = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if self.timer.isActive() or self.raw_pixmap.isNull():
            return
        steps = event.angleDelta().y() / 120
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom + steps * ZOOM_STEP))
        if self.zoom == MIN_ZOOM:
            self.pan = QPoint(0, 0)
        self._render_frame()

    # ----------------------------------------------------------- slideshow

    def show_next(self):
        self._advance(1)

    def show_previous(self):
        self._advance(-1)

    def _advance(self, step):
        if not self.image_list:
            return
        self._pending_step = step
        self.index = (self.index + step) % len(self.image_list)
        self._reset_zoom()

        animate = self.settings.get("fade", True) and not self.raw_pixmap.isNull()
        if animate and self.fade_anim.state() != QPropertyAnimation.Running:
            self.fade_anim.stop()
            self.fade_anim.setDuration(FADE_MS)
            self.fade_anim.setStartValue(self.opacity_effect.opacity())
            self.fade_anim.setEndValue(0.0)
            self.fade_anim.finished.connect(self._swap_to_current)
            self._fade_connected = True
            self.fade_anim.start()
        else:
            self._swap_to_current(fade_in=False)

    def _swap_to_current(self, fade_in=True):
        if getattr(self, "_fade_connected", False):
            self.fade_anim.finished.disconnect(self._swap_to_current)
            self._fade_connected = False

        if not self._load_current_image():
            return

        self._render_frame()
        if fade_in:
            self.fade_anim.setDuration(FADE_MS)
            self.fade_anim.setStartValue(0.0)
            self.fade_anim.setEndValue(1.0)
            self.fade_anim.start()
        else:
            self.opacity_effect.setOpacity(1.0)

    def _load_current_image(self):
        """Load image_list[self.index] into raw_pixmap, skipping unreadable
        files in the direction we were navigating. Returns False once the
        list is exhausted."""
        step = getattr(self, "_pending_step", 1) or 1
        attempts = len(self.image_list)
        while attempts > 0 and self.image_list:
            path = self.image_list[self.index]
            pixmap = load_pixmap(path)
            if not pixmap.isNull():
                self.raw_pixmap = pixmap
                filename = os.path.basename(path)
                self.info_bar.setText(
                    f" {self.index + 1} / {len(self.image_list)}   •   {filename}"
                )
                self.info_bar.adjustSize()
                return True
            del self.image_list[self.index]
            if not self.image_list:
                break
            if step < 0:
                self.index -= 1
            self.index %= len(self.image_list)
            attempts -= 1
        self.raw_pixmap = QPixmap()
        self.status_label.setText("Ingen lesbare bilder igjen.")
        self.status_label.show()
        return False

    def _reset_zoom(self, render=False):
        self.zoom = MIN_ZOOM
        self.pan = QPoint(0, 0)
        if render:
            self._render_frame()

    def _render_frame(self):
        if self.raw_pixmap.isNull():
            return
        target = self.label.size()
        base = self.raw_pixmap.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        if self.zoom <= MIN_ZOOM:
            self.label.setPixmap(base)
            return

        zoomed = self.raw_pixmap.scaled(
            target * self.zoom, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        max_x = max(0, zoomed.width() - target.width())
        max_y = max(0, zoomed.height() - target.height())
        cx = max(0, min(max_x, (zoomed.width() - target.width()) // 2 + self.pan.x()))
        cy = max(0, min(max_y, (zoomed.height() - target.height()) // 2 + self.pan.y()))
        crop = zoomed.copy(QRect(QPoint(cx, cy), target).intersected(zoomed.rect()))
        self.label.setPixmap(crop)

    # ------------------------------------------------------------ settings

    def update_interval(self, val):
        self.settings.set("interval", val)
        if self.timer.isActive():
            self.timer.start(self._interval_ms())

    def toggle_shuffle(self, state):
        self.settings.set("shuffle", state == 2)
        self.apply_sorting()

    def toggle_fade(self, state):
        self.settings.set("fade", state == 2)

    def update_sleep_timer(self, label):
        self.settings.set("sleep_timer", label)
        self._apply_sleep_timer(label)

    def toggle_pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_label.show()
            self.setCursor(Qt.ArrowCursor)
            self.menu_bar.show()
            self.mouse_timer.stop()
        else:
            self.pause_label.hide()
            self._reset_zoom(render=True)
            self.timer.start(self._interval_ms())
            self.mouse_timer.start(3000)

    def toggle_window_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # ------------------------------------------------------------ keyboard

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        elif key == Qt.Key_Space:
            self.toggle_pause()
        elif key in (Qt.Key_Right, Qt.Key_Enter, Qt.Key_Return):
            self.show_next()
        elif key == Qt.Key_Left:
            self.show_previous()
        elif key == Qt.Key_F or key == Qt.Key_F11:
            self.toggle_window_fullscreen()
        elif key in (Qt.Key_Plus, Qt.Key_Equal) and not self.timer.isActive():
            self.zoom = min(MAX_ZOOM, self.zoom + ZOOM_STEP)
            self._render_frame()
        elif key == Qt.Key_Minus and not self.timer.isActive():
            self.zoom = max(MIN_ZOOM, self.zoom - ZOOM_STEP)
            self._render_frame()
        elif key == Qt.Key_0 and not self.timer.isActive():
            self._reset_zoom(render=True)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        if self.scanner is not None and self.scanner.isRunning():
            self.scanner.requestInterruption()
            self.scanner.wait()
        super().closeEvent(event)

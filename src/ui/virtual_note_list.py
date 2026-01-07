"""
Glassnotes Virtualized Note List
Memory-efficient note list using QListWidget with custom items
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QRectF,
)
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QBrush, QPen

from src.ui.styles import GlassColors
from src.logic.file_manager import file_manager


# =============================================================================
# FUTURE: is_cloud Parameter (Google Drive)
# =============================================================================
# Status: NOT YET IMPLEMENTED - UI is hidden
# The is_cloud parameter is already implemented and waiting for ENABLE_CLOUD = True
# =============================================================================


class _ActionButton(QLabel):
    """Clickable label with animated hover effect"""

    _anim_color = QColor(0, 0, 0, 0)

    def __init__(self, text, hover_color=QColor(239, 68, 68), parent=None):
        super().__init__(text, parent)
        self._hover_color = hover_color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(24, 24)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("font-size: 14px; padding: 2px;")
        self._setup_animation()

    def _setup_animation(self):
        self._anim = QPropertyAnimation(self, b"animColor")
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _get_anim_color(self) -> QColor:
        return self._anim_color

    def _set_anim_color(self, color: QColor):
        self._anim_color = color
        self.setStyleSheet(
            f"QLabel {{ background: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()}); border-radius: 4px; }}"
        )

    animColor = pyqtProperty(QColor, fget=_get_anim_color, fset=_set_anim_color)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._anim.stop()
        self._anim.setStartValue(self._anim_color)
        self._anim.setEndValue(
            QColor(
                self._hover_color.red(),
                self._hover_color.green(),
                self._hover_color.blue(),
                40,
            )
        )
        self._anim.start()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._anim.stop()
        self._anim.setStartValue(self._anim_color)
        self._anim.setEndValue(QColor(0, 0, 0, 0))
        self._anim.start()


class NoteListItem(QFrame):
    """Lightweight note item widget with hover animation"""

    noteClicked = pyqtSignal(str)
    deleteRequested = pyqtSignal(str)
    unlinkRequested = pyqtSignal(str)

    _hover_color = QColor(0, 0, 0, 0)

    _hover_opacity = 0

    def __init__(
        self, title, path, preview="", modified_time=None, is_cloud=False, parent=None
    ):
        super().__init__(parent)
        self.path = path
        self.is_cloud = is_cloud
        self._setup_ui(title, preview, modified_time)
        self._setup_animations()
        self.setFixedHeight(110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _setup_animations(self):
        self._hover_animation = QPropertyAnimation(self, b"hoverOpacity")
        self._hover_animation.setDuration(180)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _get_hover_opacity(self) -> int:
        return self._hover_opacity

    def _set_hover_opacity(self, value: int):
        self._hover_opacity = value
        self.update()  # Trigger repaint for smooth animation without CSS overhead

    hoverOpacity = pyqtProperty(int, fget=_get_hover_opacity, fset=_set_hover_opacity)

    def paintEvent(self, event):
        """Custom paint event for silky smooth flicker-free hover animation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background highlight
        bg_alpha = int(self._hover_opacity * 0.08)
        if bg_alpha > 0:
            painter.setBrush(QBrush(QColor(157, 70, 255, bg_alpha)))
            painter.setPen(Qt.PenStyle.NoPen)
            # Draw rounded rect for background
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(2, 2, -2, -2), 6, 6
            )

        # Draw left accent strip
        if self._hover_opacity > 0:
            # Center the 60px strip vertically
            y_pos = (self.height() - 60) / 2
            accent_rect = QRectF(2, y_pos, 4, 60)
            painter.setBrush(QBrush(QColor(157, 70, 255, self._hover_opacity)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(accent_rect, 2, 2)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._animate_hover(True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._animate_hover(False)

    def _animate_hover(self, hover):
        target = 255 if hover else 0
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(target)
        self._hover_animation.start()

    def _setup_ui(self, title, preview, modified_time):
        self.setObjectName("NoteListItem")
        # Base style: transparent so we can draw the hover effect ourselves
        self.setStyleSheet("#NoteListItem { background: transparent; border: none; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 16, 0) # Clear space for the painted accent strip
        layout.setSpacing(0)

        content_container = QWidget()
        content_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(16, 14, 16, 14)
        content_layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(10)

        icon_label = QLabel()
        if self.is_cloud:
            icon_label.setText("☁️")
            icon_label.setToolTip("Cloud Note (Google Drive)")
        else:
            icon_label.setText("📄")
            icon_label.setToolTip("Local Note")
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet(
            f"color: {GlassColors.TEXT_PRIMARY}; background: transparent;"
        )

        self.delete_btn = _ActionButton("🗑️", hover_color=QColor(239, 68, 68))
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet("font-size: 14px; padding: 2px;")
        self.delete_btn.setToolTip("Delete note")
        self.delete_btn.mousePressEvent = (
            lambda e: self.deleteRequested.emit(self.path)
            if e.button() == Qt.MouseButton.LeftButton
            else None
        )

        self.unlink_btn = _ActionButton("−", hover_color=QColor(156, 163, 175))
        self.unlink_btn.setFixedSize(24, 24)
        self.unlink_btn.setStyleSheet("font-size: 16px; padding: 2px;")
        self.unlink_btn.setToolTip("Remove from history")
        self.unlink_btn.mousePressEvent = (
            lambda e: self.unlinkRequested.emit(self.path)
            if e.button() == Qt.MouseButton.LeftButton
            else None
        )

        header.addWidget(icon_label)
        header.addWidget(self.title_label, 1)
        header.addWidget(self.unlink_btn)
        header.addWidget(self.delete_btn)
        content_layout.addLayout(header)

        if preview:
            preview_text = preview[:100].replace("\n", " ").strip()
            if len(preview) > 100:
                preview_text += "..."
        else:
            preview_text = "Empty note"

        self.preview_label = QLabel(preview_text)
        self.preview_label.setFont(QFont("Segoe UI", 11))
        self.preview_label.setStyleSheet(
            f"color: {GlassColors.TEXT_TERTIARY}; background: transparent;"
        )
        self.preview_label.setWordWrap(True)
        self.preview_label.setMaximumHeight(40)
        content_layout.addWidget(self.preview_label)

        footer = QHBoxLayout()

        if modified_time:
            time_text = self._format_time(modified_time)
        else:
            time_text = "Unknown"

        self.time_label = QLabel(f"📅 {time_text}")
        self.time_label.setFont(QFont("Segoe UI", 10))
        self.time_label.setStyleSheet(
            f"color: {GlassColors.TEXT_MUTED}; background: transparent;"
        )

        footer.addWidget(self.time_label)
        footer.addStretch()
        content_layout.addLayout(footer)
        layout.addWidget(content_container, 1)

    def _format_time(self, timestamp):
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except:
                return timestamp
        elif isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
        else:
            dt = timestamp

        now = datetime.now()
        if hasattr(dt, "tzinfo") and dt.tzinfo:
            now = datetime.now(dt.tzinfo)

        diff = now - dt

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                if minutes < 2:
                    return "Just now"
                return f"{minutes} min ago"
            elif hours == 1:
                return "1 hour ago"
            return f"{hours} hours ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return dt.strftime("%b %d, %Y")

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            self.noteClicked.emit(self.path)


class VirtualNoteList(QListWidget):
    """Virtualized note list using QListWidget for memory efficiency"""

    noteClicked = pyqtSignal(str)
    deleteRequested = pyqtSignal(str)
    unlinkRequested = pyqtSignal(str)
    refreshRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VirtualNoteList")
        self._notes_data = []
        self._is_cloud = False
        self._current_sort = "recent"
        self._search_query = ""

        self._setup_ui()

    def _setup_ui(self):
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border: none;
                padding: 0px;
                margin: 6px 0px;
            }}
            QListWidget::item:selected {{
                background: transparent;
            }}
        """
        )

    def _create_item(self, note_data):
        if self._is_cloud:
            title = note_data.get("name", "Untitled")
            path = note_data.get("id", "")
            preview = ""
            modified_time = note_data.get("modifiedTime")
            is_cloud = True
        else:
            path = str(note_data)
            title = path.replace("\\", "/").split("/")[-1]
            preview = file_manager.get_file_preview(path)
            modified_time = self._get_file_modified_time(path)
            is_cloud = False

        item = QListWidgetItem()
        widget = NoteListItem(title, path, preview, modified_time, is_cloud)
        widget.noteClicked.connect(self.noteClicked.emit)
        widget.deleteRequested.connect(self.deleteRequested.emit)
        widget.unlinkRequested.connect(self.unlinkRequested.emit)

        item.setSizeHint(QSize(0, 122)) # 110 + 12 (6*2 margin)
        self.addItem(item)
        self.setItemWidget(item, widget)

    def _get_file_modified_time(self, path):
        try:
            return os.path.getmtime(path)
        except:
            return None

    def _filter_and_sort(self, notes):
        if self._search_query:
            filtered = []
            for note in notes:
                if self._is_cloud:
                    name = note.get("name", "").lower()
                else:
                    name = str(note).replace("\\", "/").split("/")[-1].lower()
                if self._search_query in name:
                    filtered.append(note)
            notes = filtered

        if self._current_sort == "name_asc":
            if self._is_cloud:
                notes = sorted(notes, key=lambda x: x.get("name", "").lower())
            else:
                notes = sorted(notes, key=lambda x: str(x).lower())
        elif self._current_sort == "name_desc":
            if self._is_cloud:
                notes = sorted(
                    notes, key=lambda x: x.get("name", "").lower(), reverse=True
                )
            else:
                notes = sorted(notes, key=lambda x: str(x).lower(), reverse=True)

        return notes

    def set_notes(self, notes, is_cloud=False, sort="recent", search=""):
        """Set notes data and rebuild list"""
        self._notes_data = notes
        self._is_cloud = is_cloud
        self._current_sort = sort
        self._search_query = search.lower().strip() if search else ""

        self.clear()

        filtered = self._filter_and_sort(self._notes_data)

        for note in filtered:
            self._create_item(note)

        if not filtered:
            self._show_empty_state()

    def _show_empty_state(self):
        item = QListWidgetItem()
        empty_widget = QLabel(
            "No notes found" if self._search_query else "No notes yet"
        )
        empty_widget.setObjectName("EmptyState")
        empty_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_widget.setStyleSheet(
            f"color: {GlassColors.TEXT_MUTED}; font-size: 14px; padding: 20px;"
        )
        empty_widget.setFixedHeight(80)
        item.setSizeHint(QSize(0, 80))
        self.addItem(item)
        self.setItemWidget(item, empty_widget)

    def count_notes(self):
        return len(
            [
                i
                for i in range(self.count())
                if self.itemWidget(self.item(i)) is not None
            ]
        )

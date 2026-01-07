"""
Glassnotes Hub View
Premium glassmorphism hub with search, filtering, and virtualized note list
"""

import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QMessageBox,
    QSizePolicy,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from qfluentwidgets import (
    PrimaryPushButton,
    FluentIcon as FIF,
    LineEdit,
    ComboBox,
    PushButton,
    InfoBar,
)

from src.ui.styles import get_hub_style, GlassColors
from src.logic.config import config, ENABLE_CLOUD
from src.logic.file_manager import file_manager
from src.ui.virtual_note_list import VirtualNoteList, _ActionButton


# =============================================================================
# FUTURE: Cloud Notes Section (Google Drive)
# =============================================================================
# Status: NOT YET IMPLEMENTED - UI is hidden
# To enable: Set ENABLE_CLOUD = True in src/logic/config.py
# =============================================================================


class HubView(QFrame):
    """Premium glassmorphism hub with virtualized note list and scrollable content"""

    open_note = pyqtSignal(str)
    new_note = pyqtSignal()
    open_file_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    file_deleted = pyqtSignal(str)
    unlink_all_requested = pyqtSignal()
    delete_all_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HubView")
        self._local_notes = []
        self._current_sort = "recent"
        self._search_query = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 40, 48, 40)
        layout.setSpacing(28)

        self.setStyleSheet(get_hub_style())

        self._create_header(layout)
        self._create_search_bar(layout)

        self._create_scroll_content(layout)

    def _create_scroll_content(self, parent_layout):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 16, 0)
        scroll_layout.setSpacing(20)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(24)

        self.local_list = VirtualNoteList()
        self.local_list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.local_list.noteClicked.connect(self.open_note.emit)
        self.local_list.deleteRequested.connect(self.delete_note)
        self.local_list.unlinkRequested.connect(self.unlink_note)
        self.local_list.refreshRequested.connect(self.refresh_requested.emit)

        local_container, card, local_count = self._create_section_container(
            "Local Notes", "📁", "Your notes saved locally", show_unlink_all=True
        )

        content_layout.addWidget(local_container, 1)
        card.layout().addWidget(self.local_list)

        self.local_count_badge = local_container.findChild(QLabel, "count_badge")
        self.local_unlink_all_btn = local_container.findChild(QLabel, "unlink_all_btn")
        self.local_delete_all_btn = local_container.findChild(QLabel, "delete_all_btn")

        scroll_layout.addLayout(content_layout)

        scroll.setWidget(scroll_content)
        parent_layout.addWidget(scroll, 1)

    def _create_header(self, parent_layout):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        title_container = QVBoxLayout()
        title_container.setSpacing(4)

        title = QLabel("Glassnotes")
        title.setObjectName("WelcomeTitle")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))

        subtitle = QLabel("Your notes, beautifully organized")
        subtitle.setObjectName("WelcomeSubtitle")

        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        header_layout.addLayout(title_container)

        header_layout.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(12)

        refresh_btn = PushButton(FIF.SYNC, "Refresh")
        refresh_btn.setToolTip("Refresh notes list")
        refresh_btn.clicked.connect(self.refresh_requested.emit)

        new_btn = PrimaryPushButton(FIF.ADD, "New Note")
        new_btn.setFixedHeight(42)
        new_btn.clicked.connect(self.new_note.emit)

        open_btn = PushButton(FIF.FOLDER, "Open File")
        open_btn.setFixedHeight(42)
        open_btn.setToolTip("Open external file")
        open_btn.clicked.connect(self.open_file_requested.emit)

        actions.addWidget(refresh_btn)
        actions.addWidget(open_btn)
        actions.addWidget(new_btn)
        header_layout.addLayout(actions)

        parent_layout.addWidget(header_widget)

    def _create_search_bar(self, parent_layout):
        search_container = QWidget()
        search_container.setObjectName("SearchContainer")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(8, 8, 8, 8)
        search_layout.setSpacing(16)

        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self._on_search)

        self.sort_combo = ComboBox()
        self.sort_combo.addItems(["Recent First", "Name (A-Z)", "Name (Z-A)"])
        self.sort_combo.setFixedWidth(150)
        self.sort_combo.setFixedHeight(38)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.sort_combo)

        parent_layout.addWidget(search_container)

    def _create_section_container(
        self, title, icon, description, show_unlink_all=False
    ):
        container = QWidget()
        container.setObjectName("SettingsSection")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(12)
        header.setContentsMargins(8, 0, 8, 4)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 22px; background: transparent;")

        title_label = QLabel(title)
        title_label.setObjectName("SectionHeader")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))

        count_badge = QLabel("0")
        count_badge.setObjectName("count_badge")
        count_badge.setStyleSheet("""
            background: rgba(157, 70, 255, 0.2);
            color: #B76EFF;
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 12px;
            font-weight: 600;
        """)

        unlink_all_btn = None
        delete_all_btn = None
        if show_unlink_all:
            unlink_all_btn = _ActionButton("−", hover_color=QColor(156, 163, 175))
            unlink_all_btn.setObjectName("unlink_all_btn")
            unlink_all_btn.setStyleSheet("font-size: 16px; padding: 2px;")
            unlink_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            unlink_all_btn.hide()
            unlink_all_btn.mousePressEvent = (
                lambda e: self.unlink_all_requested.emit()
                if e.button() == Qt.MouseButton.LeftButton
                else None
            )

            delete_all_btn = _ActionButton("🗑️", hover_color=QColor(239, 68, 68))
            delete_all_btn.setObjectName("delete_all_btn")
            delete_all_btn.setStyleSheet("font-size: 14px; padding: 2px;")
            delete_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_all_btn.hide()
            delete_all_btn.mousePressEvent = (
                lambda e: self.delete_all_requested.emit()
                if e.button() == Qt.MouseButton.LeftButton
                else None
            )

        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addWidget(count_badge)
        header.addStretch()
        if unlink_all_btn:
            header.addWidget(unlink_all_btn)
        if delete_all_btn:
            header.addWidget(delete_all_btn)
        layout.addLayout(header)

        card = QFrame()
        card.setObjectName("SettingsCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(16)

        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(card)
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        return container, card, count_badge

    def _on_search(self, text):
        self._search_query = text.lower().strip()
        self._refresh_display()

    def _on_sort_changed(self, index):
        sort_options = ["recent", "name_asc", "name_desc"]
        self._current_sort = sort_options[index]
        self._refresh_display()

    def _refresh_display(self):
        self.update_recent_list(self._local_notes, skip_store=True)

    def delete_note(self, path):
        name = os.path.basename(path)
        reply = QMessageBox.question(
            self,
            "Delete Note",
            f"Are you sure you want to delete '{name}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if file_manager.delete_file(path):
                config.remove_recent_file(path)
                self.file_deleted.emit(path)
                self.refresh_requested.emit()
                InfoBar.success(
                    "Deleted", "Note deleted successfully", duration=2000, parent=self
                )
            else:
                InfoBar.error(
                    "Error", "Failed to delete note", duration=2000, parent=self
                )

    def unlink_note(self, path):
        name = os.path.basename(path)
        reply = QMessageBox.question(
            self,
            "Remove from History",
            f"Remove '{name}' from history?\nThe file will be kept on your system.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            config.remove_recent_file(path)
            self.refresh_requested.emit()
            InfoBar.info(
                "Removed", f"'{name}' removed from history", duration=2000, parent=self
            )

    def unlink_all_notes(self):
        count = len(self._local_notes)
        if count == 0:
            return

        reply = QMessageBox.question(
            self,
            "Remove All from History",
            f"Remove all {count} notes from history?\nFiles will be kept on your system.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for path in self._local_notes:
                config.remove_recent_file(path)
            self.refresh_requested.emit()
            InfoBar.info(
                "Removed All",
                f"{count} notes removed from history",
                duration=3000,
                parent=self,
            )

    def delete_all_notes(self):
        count = len(self._local_notes)
        if count == 0:
            return

        reply = QMessageBox.question(
            self,
            "Delete All Notes",
            f"Delete all {count} notes from your system?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for path in self._local_notes:
                file_manager.delete_file(path)
                config.remove_recent_file(path)
                self.file_deleted.emit(path)
            self.refresh_requested.emit()
            InfoBar.success(
                "Deleted All",
                f"{count} notes deleted successfully",
                duration=3000,
                parent=self,
            )

    def update_recent_list(self, recent_files, skip_store=False):
        if not skip_store:
            self._local_notes = recent_files or []

        sort = self._current_sort
        search = self._search_query

        if self.local_count_badge:
            self.local_count_badge.setText(str(len(self._local_notes)))

        self.local_list.set_notes(
            self._local_notes, is_cloud=False, sort=sort, search=search
        )

        if self.local_unlink_all_btn:
            self.local_unlink_all_btn.setVisible(len(self._local_notes) > 0)
        if self.local_delete_all_btn:
            self.local_delete_all_btn.setVisible(len(self._local_notes) > 0)

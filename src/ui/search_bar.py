"""
Glassnotes Search Bar
Integrated search panel with find functionality
"""

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QToolButton,
    QCheckBox,
    QLabel,
    QFrame,
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from qfluentwidgets import TransparentToolButton, FluentIcon as FIF

from src.ui.styles import GlassColors, GlassEffects


class SearchBar(QWidget):
    """Integrated search bar with find functionality"""

    search_next = pyqtSignal(str)  # Search text
    search_previous = pyqtSignal(str)
    search_changed = pyqtSignal(str)  # For live highlighting
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()

        self._case_sensitive = False
        self._current_matches = []
        self._current_match_index = -1

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        # Search icon
        self.search_icon = TransparentToolButton(FIF.SEARCH)
        self.search_icon.setFixedSize(28, 28)
        self.search_icon.setIconSize(QSize(16, 16))
        self.search_icon.setToolTip("Search")
        layout.addWidget(self.search_icon)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedWidth(280)
        self.search_input.setObjectName("SearchInput")
        layout.addWidget(self.search_input)

        # Match count label
        self.match_label = QLabel("0 matches")
        self.match_label.setStyleSheet(f"""
            color: {GlassColors.TEXT_TERTIARY};
            font-size: 11px;
            min-width: 70px;
        """)
        layout.addWidget(self.match_label)

        layout.addSpacing(8)

        # Navigation buttons
        self.prev_btn = TransparentToolButton(FIF.UP)
        self.prev_btn.setFixedSize(28, 28)
        self.prev_btn.setIconSize(QSize(14, 14))
        self.prev_btn.setToolTip("Find Previous (Shift+F3)")
        layout.addWidget(self.prev_btn)

        self.next_btn = TransparentToolButton(FIF.DOWN)
        self.next_btn.setFixedSize(28, 28)
        self.next_btn.setIconSize(QSize(14, 14))
        self.next_btn.setToolTip("Find Next (F3)")
        layout.addWidget(self.next_btn)

        layout.addSpacing(8)

        # Options divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet(f"""
            QFrame {{
                background: {GlassColors.GLASS_BORDER};
                width: 1px;
            }}
        """)
        layout.addWidget(divider)

        # Case sensitive checkbox
        self.case_checkbox = QCheckBox("Case")
        self.case_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {GlassColors.TEXT_SECONDARY};
                font-size: 11px;
                spacing: 4px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 1px solid {GlassColors.GLASS_BORDER};
                border-radius: 3px;
                background: rgba(255, 255, 255, 0.05);
            }}
            QCheckBox::indicator:checked {{
                border: 1px solid {GlassColors.PRIMARY};
                border-radius: 3px;
                background: {GlassColors.PRIMARY};
            }}
        """)
        layout.addWidget(self.case_checkbox)

        # Whole word checkbox
        self.whole_word_checkbox = QCheckBox("Whole word")
        self.whole_word_checkbox.setStyleSheet(self.case_checkbox.styleSheet())
        layout.addWidget(self.whole_word_checkbox)

        layout.addStretch()

        # Close button
        self.close_btn = TransparentToolButton(FIF.CLOSE)
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setIconSize(QSize(14, 14))
        self.close_btn.setToolTip("Close Search (Esc)")
        layout.addWidget(self.close_btn)

        # Apply container style
        self.setStyleSheet(f"""
            SearchBar {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 22, 50, 0.95),
                    stop:1 rgba(20, 15, 35, 0.95)
                );
                border-top: 1px solid {GlassColors.GLASS_BORDER};
            }}
        """)

    def _setup_connections(self):
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self._on_return_pressed)
        self.prev_btn.clicked.connect(self._on_prev_clicked)
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.case_checkbox.toggled.connect(self._on_options_changed)
        self.whole_word_checkbox.toggled.connect(self._on_options_changed)
        self.close_btn.clicked.connect(self.close_requested.emit)

    def _on_text_changed(self, text):
        if text:
            self.search_changed.emit(text)
        else:
            self.match_label.setText("0 matches")
            self._current_matches = []
            self._current_match_index = -1

    def _on_return_pressed(self):
        text = self.search_input.text()
        if text:
            self.search_next.emit(text)

    def _on_prev_clicked(self):
        text = self.search_input.text()
        if text:
            self.search_previous.emit(text)

    def _on_next_clicked(self):
        text = self.search_input.text()
        if text:
            self.search_next.emit(text)

    def _on_options_changed(self):
        text = self.search_input.text()
        if text:
            self.search_changed.emit(text)

    def set_match_count(self, count, current_index=-1):
        """Update the match count display"""
        self._current_matches = list(range(count))
        self._current_match_index = current_index

        if count == 0:
            self.match_label.setText("No matches")
            self.match_label.setStyleSheet(f"""
                color: {GlassColors.ERROR};
                font-size: 11px;
                min-width: 70px;
            """)
        elif current_index >= 0:
            self.match_label.setText(f"{current_index + 1}/{count}")
            self.match_label.setStyleSheet(f"""
                color: {GlassColors.SUCCESS};
                font-size: 11px;
                min-width: 70px;
            """)
        else:
            self.match_label.setText(f"{count} matches")
            self.match_label.setStyleSheet(f"""
                color: {GlassColors.TEXT_SECONDARY};
                font-size: 11px;
                min-width: 70px;
            """)

    def focus_search_input(self):
        """Focus the search input field"""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def get_search_text(self):
        """Get current search text"""
        return self.search_input.text()

    def is_case_sensitive(self):
        """Check if case sensitive is enabled"""
        return self.case_checkbox.isChecked()

    def is_whole_word(self):
        """Check if whole word is enabled"""
        return self.whole_word_checkbox.isChecked()

    def close_search(self):
        """Clear search and close"""
        self.search_input.clear()
        self.match_label.setText("0 matches")
        self.close_requested.emit()

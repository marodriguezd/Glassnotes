"""
Glassnotes Premium Editor
Professional text editor with line numbers, current line highlighting, and modern typography
"""

from PyQt6.QtWidgets import (
    QWidget,
    QPlainTextEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtGui import (
    QFont,
    QTextOption,
    QColor,
    QPainter,
    QTextFormat,
    QTextCharFormat,
    QFontDatabase,
    QPen,
    QTextCursor,
)
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal

from src.ui.styles import get_editor_style, GlassColors
from src.logic.config import config


class LineNumberArea(QWidget):
    """Line number gutter for the editor"""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setStyleSheet(f"""
            background: rgba(20, 15, 35, 0.9);
            border: none;
        """)

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class Editor(QPlainTextEdit):
    """Premium glassmorphism text editor with line numbers and enhancements"""

    word_count_changed = pyqtSignal(int, int)  # words, characters
    cursor_position_changed = pyqtSignal(int, int)  # line, column
    search_highlight_changed = pyqtSignal(int, int)  # match_count, current_index

    def __init__(self, content="", parent=None):
        super().__init__(parent)

        # File tracking
        self.file_path = None
        # =============================================================================
        # FUTURE: drive_id Attribute (Google Drive)
        # =============================================================================
        # Status: NOT YET IMPLEMENTED - UI is hidden
        # To enable: Set ENABLE_CLOUD = True in src/logic/config.py
        # =============================================================================
        self.drive_id = None

        # Search state
        self._search_matches = []
        self._current_match_index = -1
        self._last_search_text = ""

        # Setup
        self._setup_font()
        self._setup_editor()
        self._setup_line_numbers()
        self._setup_styling()

        # Set initial content
        self.setPlainText(content)
        self._update_counts()

    def _setup_font(self):
        """Setup modern monospace font with fallbacks"""
        # Try to use premium coding fonts
        preferred_fonts = [
            "JetBrains Mono",
            "Cascadia Code",
            "Fira Code",
            "Source Code Pro",
            "Consolas",
        ]

        # In PyQt6, QFontDatabase methods are static
        available_fonts = QFontDatabase.families()

        selected_font = "Consolas"  # Fallback
        for font_name in preferred_fonts:
            if font_name in available_fonts:
                selected_font = font_name
                break

        # Use size from config
        font_size = config.get("font_size", 13)
        if font_size <= 0:
            font_size = 13

        self.editor_font = QFont(selected_font, font_size)
        self.editor_font.setStyleHint(QFont.StyleHint.Monospace)
        self.editor_font.setFixedPitch(True)
        self.setFont(self.editor_font)

    def _setup_editor(self):
        """Configure editor behavior"""
        self.setPlaceholderText("Start writing your note...")
        self.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)

        # Cursor shape
        self.setCursorWidth(2)

        # Connect signals
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.cursorPositionChanged.connect(self._emit_cursor_position)
        self.textChanged.connect(self._update_counts)

    def _setup_line_numbers(self):
        """Setup line number gutter"""
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)

        self._update_line_number_area_width(0)

    def _setup_styling(self):
        """Apply premium glassmorphism styling"""
        self.setObjectName("NoteEditor")

        # Static background style
        accent = self._get_accent_color()
        accent_rgb = f"{accent.red()}, {accent.green()}, {accent.blue()}"

        self.setStyleSheet(f"""
            #NoteEditor {{
                background-color: rgb(25, 20, 40);
                border: none;
                border-radius: 0px;
                padding: 0px;
                padding-left: 8px;
                color: {GlassColors.TEXT_PRIMARY};
                selection-background-color: rgba({accent_rgb}, 0.4);
                selection-color: {GlassColors.TEXT_PRIMARY};
            }}
        """)

        # Initial line highlight
        self._highlight_current_line()

    def _get_accent_color(self):
        """Get current accent color from settings"""
        return QColor(config.settings.get("accent_color", "#9D46FF"))

    def line_number_area_width(self):
        """Calculate width needed for line numbers"""
        digits = 1
        max_block = max(1, self.blockCount())
        while max_block >= 10:
            max_block //= 10
            digits += 1

        # Minimum 3 digits wide, plus padding
        digits = max(3, digits)
        space = 24 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def _update_line_number_area_width(self, _):
        """Update viewport margins for line numbers"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        """Update line number area on scroll"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize to update line number area"""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        """Paint line numbers with dynamic accent color"""
        painter = QPainter(self.line_number_area)

        # Background - slightly lighter purple-tinted dark
        painter.fillRect(event.rect(), QColor(20, 16, 35))

        # Get dynamic accent color
        accent = self._get_accent_color()

        # Draw border line with accent color
        border_pen = QPen(accent, 1)
        border_color = QColor(accent)
        border_color.setAlpha(60)  # Reduced opacity for border
        painter.setPen(border_color)

        painter.drawLine(
            event.rect().right(),
            event.rect().top(),
            event.rect().right(),
            event.rect().bottom(),
        )

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        current_block = self.textCursor().block().blockNumber()

        # Set font for numbers
        number_font = QFont(self.editor_font)
        # Use a slightly smaller font than the editor
        # Ensure we don't pass -1 if pointSize() is undefined (uses pixels)
        base_size = self.editor_font.pointSize()
        if base_size <= 0:
            base_size = self.editor_font.pixelSize()
        if base_size <= 0:
            base_size = 13

        num_size = max(1, base_size - 2)
        number_font.setPointSize(num_size)
        painter.setFont(number_font)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                # Highlight current line number with dynamic accent
                if block_number == current_block:
                    # Current line: bright accent color
                    painter.setPen(accent)
                else:
                    # Other lines: softer version of accent color
                    soft_accent = QColor(accent)
                    soft_accent.setAlpha(150)  # More transparent
                    painter.setPen(soft_accent)

                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 12,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def _highlight_current_line(self):
        """Highlight the current line with subtle accent glow"""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            # Subtle accent highlight for current line
            accent = self._get_accent_color()
            line_color = QColor(accent)
            line_color.setAlpha(25)  # Very subtle background

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()

            extra_selections.append(selection)

            # Repaint line numbers to update highlight
            self.line_number_area.update()

        self.setExtraSelections(extra_selections)

        self.setExtraSelections(extra_selections)

    def _emit_cursor_position(self):
        """Emit current cursor position"""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)

    def _update_counts(self):
        """Update and emit word/character counts"""
        text = self.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        self.word_count_changed.emit(word_count, char_count)

    def set_content(self, text):
        """Set editor content"""
        self.setPlainText(text)

    def get_content(self):
        """Get editor content"""
        return self.toPlainText()

    def set_font_size(self, size):
        """Change font size"""
        target_size = max(1, int(size))
        self.editor_font.setPointSize(target_size)
        self.setFont(self.editor_font)

        # Update line number font
        number_font = QFont(self.editor_font)
        number_font.setPointSize(max(1, target_size - 1))

        # Trigger updates
        self._update_line_number_area_width(0)
        self.line_number_area.update()

    def zoom_in(self):
        """Increase font size"""
        current_size = self.editor_font.pointSize()
        if current_size < 32:
            self.set_font_size(current_size + 1)

    def zoom_out(self):
        """Decrease font size"""
        current_size = self.editor_font.pointSize()
        if current_size > 8:
            self.set_font_size(current_size - 1)

    def _find_all_matches(self, text, case_sensitive=False, whole_word=False):
        """Find all occurrences of text in the document"""
        import re

        matches = []
        if not text:
            return matches

        content = self.toPlainText()

        if whole_word:
            pattern = r"\b" + re.escape(text) + r"\b"
        else:
            pattern = re.escape(text)

        flags = 0 if case_sensitive else re.IGNORECASE
        for match in re.finditer(pattern, content, flags):
            matches.append(match.start())

        return matches

    def _highlight_search_matches(self, text, case_sensitive=False, whole_word=False):
        """Highlight all search matches"""
        self._clear_search_highlights()

        if not text:
            self._search_matches = []
            self._current_match_index = -1
            self.search_highlight_changed.emit(0, -1)
            return

        self._search_matches = self._find_all_matches(text, case_sensitive, whole_word)

        if not self._search_matches:
            self._current_match_index = -1
            self.search_highlight_changed.emit(0, -1)
            self._highlight_current_line()
            return

        self._current_match_index = -1
        extra_selections = []

        accent = self._get_accent_color()
        highlight_color = QColor(accent)
        highlight_color.setAlpha(60)

        for pos in self._search_matches:
            selection = QTextEdit.ExtraSelection()
            cursor = self.textCursor()
            cursor.setPosition(pos)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(text),
            )
            selection.cursor = cursor
            selection.format.setBackground(highlight_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, False)
            extra_selections.append(selection)

        current_line_selections = self._get_current_line_selection()
        extra_selections.extend(current_line_selections)

        self.setExtraSelections(extra_selections)
        self.search_highlight_changed.emit(len(self._search_matches), -1)

    def _clear_search_highlights(self):
        """Clear all search highlights"""
        self._highlight_current_line()

    def _get_current_line_selection(self):
        """Get the current line highlight selection"""
        selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            accent = self._get_accent_color()
            line_color = QColor(accent)
            line_color.setAlpha(25)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)
        return selections

    def find_next(self, text, case_sensitive=False, whole_word=False, wrap=True):
        """Find next occurrence of text"""
        if not text:
            return False

        if not self._search_matches or self._last_search_text != text:
            self._search_matches = self._find_all_matches(
                text, case_sensitive, whole_word
            )
            self._last_search_text = text
            self._current_match_index = -1

        if not self._search_matches:
            return False

        content = self.toPlainText()
        cursor_pos = self.textCursor().position()

        next_index = -1
        for i, pos in enumerate(self._search_matches):
            if pos > cursor_pos:
                next_index = i
                break

        if next_index == -1:
            if wrap:
                next_index = 0
            else:
                return False

        self._current_match_index = next_index
        self._select_match(next_index)
        self._highlight_search_matches(text, case_sensitive, whole_word)
        return True

    def find_previous(self, text, case_sensitive=False, whole_word=False, wrap=True):
        """Find previous occurrence of text"""
        if not text:
            return False

        if not self._search_matches or self._last_search_text != text:
            self._search_matches = self._find_all_matches(
                text, case_sensitive, whole_word
            )
            self._last_search_text = text
            self._current_match_index = -1

        if not self._search_matches:
            return False

        cursor_pos = self.textCursor().position()

        prev_index = -1
        for i in range(len(self._search_matches) - 1, -1, -1):
            pos = self._search_matches[i]
            if pos < cursor_pos:
                prev_index = i
                break

        if prev_index == -1:
            if wrap:
                prev_index = len(self._search_matches) - 1
            else:
                return False

        self._current_match_index = prev_index
        self._select_match(prev_index)
        self._highlight_search_matches(text, case_sensitive, whole_word)
        return True

    def _select_match(self, index):
        """Select the match at the given index"""
        if index < 0 or index >= len(self._search_matches):
            return

        pos = self._search_matches[index]
        text = self._last_search_text
        length = len(text)

        cursor = self.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, length
        )
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

        self.search_highlight_changed.emit(len(self._search_matches), index)

    def clear_search_state(self):
        """Clear search state and highlights"""
        self._search_matches = []
        self._current_match_index = -1
        self._last_search_text = ""
        self._clear_search_highlights()

    def wheelEvent(self, event):
        """Handle ctrl+wheel for zoom"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

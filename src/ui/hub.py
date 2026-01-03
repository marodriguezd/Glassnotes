"""
Glassnotes Hub View
Premium glassmorphism hub with search, filtering, and enhanced note cards
"""
import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QScrollArea, QFrame, QSizePolicy, QGraphicsDropShadowEffect, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QColor, QFont
from qfluentwidgets import (PrimaryPushButton, SubtitleLabel, FluentIcon as FIF, 
                             CardWidget, LineEdit, ComboBox, PushButton, 
                             TransparentToolButton, ToolTipFilter, ToolTipPosition, InfoBar)

from src.ui.styles import get_note_card_style, get_hub_style, GlassColors
from src.logic.config import config
from src.logic.file_manager import file_manager


class NoteCard(CardWidget):
    """Premium glassmorphism note card with preview and metadata"""
    noteClicked = pyqtSignal(str)
    deleteRequested = pyqtSignal(str)
    
    def __init__(self, title, path, preview="", modified_time=None, is_cloud=False, parent=None):
        super().__init__(parent)
        self.path = path
        self.is_cloud = is_cloud
        self._setup_ui(title, preview, modified_time)
        self._setup_effects()
        self.setStyleSheet(get_note_card_style())
        
    def _setup_ui(self, title, preview, modified_time):
        self.setFixedHeight(110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        
        # Header row with title and icon
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Cloud/Local indicator icon
        icon_label = QLabel()
        if self.is_cloud:
            icon_label.setText("☁️")
            icon_label.setToolTip("Cloud Note (Google Drive)")
        else:
            icon_label.setText("📄")
            icon_label.setToolTip("Local Note")
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet(f"color: {GlassColors.TEXT_PRIMARY}; background: transparent;")
        
        # Delete Button
        self.delete_btn = TransparentToolButton(FIF.DELETE, self)
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.setToolTip("Delete Note")
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        # Custom style for red hover effect
        self.delete_btn.setStyleSheet("""
            TransparentToolButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 4px;
            }
            TransparentToolButton:hover {
                background: rgba(239, 68, 68, 0.2); 
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
        """)
        
        header.addWidget(icon_label)
        header.addWidget(self.title_label, 1)
        header.addWidget(self.delete_btn)
        layout.addLayout(header)


        
        # Preview snippet
        if preview:
            preview_text = preview[:100].replace('\n', ' ').strip()
            if len(preview) > 100:
                preview_text += "..."
        else:
            preview_text = "Empty note"
            
        self.preview_label = QLabel(preview_text)
        self.preview_label.setFont(QFont("Segoe UI", 11))
        self.preview_label.setStyleSheet(f"color: {GlassColors.TEXT_TERTIARY}; background: transparent;")
        self.preview_label.setWordWrap(True)
        self.preview_label.setMaximumHeight(40)
        layout.addWidget(self.preview_label)
        
        # Footer with metadata
        footer = QHBoxLayout()
        
        # Modified time
        if modified_time:
            time_text = self._format_time(modified_time)
        else:
            time_text = "Unknown"
            
        self.time_label = QLabel(f"📅 {time_text}")
        self.time_label.setFont(QFont("Segoe UI", 10))
        self.time_label.setStyleSheet(f"color: {GlassColors.TEXT_MUTED}; background: transparent;")
        
        footer.addWidget(self.time_label)
        footer.addStretch()
        layout.addLayout(footer)
        
    def _on_delete_clicked(self):
        self.deleteRequested.emit(self.path)

    def _format_time(self, timestamp):
        """Format timestamp to human-readable relative time"""
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return timestamp
        elif isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
        else:
            dt = timestamp
            
        now = datetime.now()
        if hasattr(dt, 'tzinfo') and dt.tzinfo:
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
    
    def _setup_effects(self):
        """Setup hover glow effect"""
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor(157, 70, 255, 0))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        
    def enterEvent(self, event):
        """Animate glow on hover"""
        super().enterEvent(event)
        # Animate shadow
        self.shadow.setBlurRadius(25)
        self.shadow.setColor(QColor(157, 70, 255, 80))
        
    def leaveEvent(self, event):
        """Remove glow on leave"""
        super().leaveEvent(event)
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor(157, 70, 255, 0))
        
    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            self.noteClicked.emit(self.path)


class HubView(QWidget):
    """Premium glassmorphism hub with search, sorting, and enhanced UX"""
    open_note = pyqtSignal(str)
    new_note = pyqtSignal()
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HubView")
        self._local_notes = []
        self._cloud_notes = []
        self._current_sort = "recent"
        self._search_query = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 40, 48, 40)
        layout.setSpacing(28)
        
        # Apply hub styling
        self.setStyleSheet(get_hub_style())
        
        # === HEADER SECTION ===
        self._create_header(layout)
        
        # === SEARCH & FILTER BAR ===
        self._create_search_bar(layout)
        
        # === CONTENT SECTIONS ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        
        # Local Notes Section
        self.local_section, self.local_list_layout = self._create_section(
            "Local Notes", "📁", "Your notes saved locally"
        )
        self.local_count_badge = self.local_section.findChild(QLabel, "count_badge")
        
        # Cloud Notes Section  
        self.cloud_section, self.cloud_list_layout = self._create_section(
            "Cloud Notes", "☁️", "Notes synced with Google Drive"
        )
        self.cloud_count_badge = self.cloud_section.findChild(QLabel, "count_badge")
        
        # Login button for cloud section
        self.login_btn = PrimaryPushButton(FIF.PEOPLE, "Connect Google Drive")
        self.login_btn.setFixedHeight(42)
        login_container = self.cloud_section.findChild(QWidget, "login_container")
        if login_container:
            login_container.layout().addWidget(self.login_btn)
        
        content_layout.addWidget(self.local_section, 1)
        # content_layout.addWidget(self.cloud_section, 1)
        layout.addLayout(content_layout)
        
    def _create_header(self, parent_layout):
        """Create premium header with title and action buttons"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)
        
        # Left side - Title and subtitle
        title_container = QVBoxLayout()
        title_container.setSpacing(4)
        
        title = QLabel("✨ Glassnotes")
        title.setObjectName("WelcomeTitle")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        
        subtitle = QLabel("Your notes, beautifully organized")
        subtitle.setObjectName("WelcomeSubtitle")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        header_layout.addLayout(title_container)
        
        header_layout.addStretch()
        
        # Right side - Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(12)
        
        # Refresh button
        refresh_btn = PushButton(FIF.SYNC, "Refresh")
        refresh_btn.setToolTip("Refresh notes list")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        
        # New Note button (primary)
        new_btn = PrimaryPushButton(FIF.ADD, "New Note")
        new_btn.setFixedHeight(42)
        new_btn.clicked.connect(self.new_note.emit)
        
        actions.addWidget(refresh_btn)
        actions.addWidget(new_btn)
        header_layout.addLayout(actions)
        
        parent_layout.addWidget(header_widget)
        
    def _create_search_bar(self, parent_layout):
        """Create search and filter bar"""
        search_container = QWidget()
        search_container.setObjectName("SearchContainer")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(8, 8, 8, 8)
        search_layout.setSpacing(16)
        
        # Search input
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("🔍 Search notes...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self._on_search)
        
        # Sort dropdown
        self.sort_combo = ComboBox()
        self.sort_combo.addItems(["Recent First", "Name (A-Z)", "Name (Z-A)"])
        self.sort_combo.setFixedWidth(150)
        self.sort_combo.setFixedHeight(38)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.sort_combo)
        
        parent_layout.addWidget(search_container)
        
    def _create_section(self, title, icon, description):
        """Create a notes section with header, scroll area, and content"""
        container = QWidget()
        container.setObjectName("SectionContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Section header
        header = QHBoxLayout()
        header.setSpacing(12)
        
        # Icon and title
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 22px; background: transparent;")
        
        title_label = QLabel(title)
        title_label.setObjectName("SectionHeader")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))
        
        # Count badge
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
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addWidget(count_badge)
        header.addStretch()
        layout.addLayout(header)
        
        # Login container (for cloud section)
        login_container = QWidget()
        login_container.setObjectName("login_container")
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(login_container)
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 8, 0)
        content_layout.setSpacing(12)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll, 1)
        
        return container, content_layout
        
    def _on_search(self, text):
        """Handle search input changes"""
        self._search_query = text.lower().strip()
        self._refresh_display()
        
    def _on_sort_changed(self, index):
        """Handle sort selection changes"""
        sort_options = ["recent", "name_asc", "name_desc"]
        self._current_sort = sort_options[index]
        self._refresh_display()
        
    def _refresh_display(self):
        """Refresh the display based on current search and sort settings"""
        self.update_recent_list(self._local_notes, skip_store=True)
        self.update_cloud_list(self._cloud_notes, skip_store=True)
        
    def _filter_and_sort(self, notes, is_cloud=False):
        """Filter and sort notes based on current settings"""
        # Filter by search query
        if self._search_query:
            filtered = []
            for note in notes:
                if is_cloud:
                    name = note.get('name', '').lower()
                else:
                    name = str(note).replace("\\", "/").split('/')[-1].lower()
                if self._search_query in name:
                    filtered.append(note)
            notes = filtered
            
        # Sort
        if self._current_sort == "name_asc":
            if is_cloud:
                notes = sorted(notes, key=lambda x: x.get('name', '').lower())
            else:
                notes = sorted(notes, key=lambda x: str(x).lower())
        elif self._current_sort == "name_desc":
            if is_cloud:
                notes = sorted(notes, key=lambda x: x.get('name', '').lower(), reverse=True)
            else:
                notes = sorted(notes, key=lambda x: str(x).lower(), reverse=True)
        # "recent" keeps original order
        
        return notes
    
    def _get_file_preview(self, path):
        """Get first few lines of a file as preview"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read(200)
                return content
        except:
            return ""
            
    def _get_file_modified_time(self, path):
        """Get file modification time"""
        try:
            return os.path.getmtime(path)
        except:
            return None

    def delete_note(self, path):
        """Delete a local note"""
        name = os.path.basename(path)
        reply = QMessageBox.question(
            self, 
            "Delete Note", 
            f"Are you sure you want to delete '{name}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if file_manager.delete_file(path):
                # Remove from recent files config
                config.remove_recent_file(path)
                
                # Refresh list
                self.refresh_requested.emit()
                
                InfoBar.success(
                    "Deleted",
                    "Note deleted successfully",
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.error(
                    "Error",
                    "Failed to delete note",
                    duration=2000,
                    parent=self
                )

    def update_cloud_list(self, drive_notes, skip_store=False):
        """Update cloud notes display"""
        if not skip_store:
            self._cloud_notes = drive_notes or []
            
        # Clear layout
        while self.cloud_list_layout.count():
            item = self.cloud_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        notes = self._filter_and_sort(self._cloud_notes, is_cloud=True)
        
        # Update count badge
        if self.cloud_count_badge:
            self.cloud_count_badge.setText(str(len(notes)))
            
        if not notes:
            empty = QLabel("No cloud notes found" if self._cloud_notes else "Connect Google Drive to sync notes")
            empty.setObjectName("EmptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cloud_list_layout.addWidget(empty)
        else:
            for note in notes:
                card = NoteCard(
                    title=note.get('name', 'Untitled'),
                    path=note.get('id', ''),
                    preview="",  # Cloud notes don't have preview without downloading
                    modified_time=note.get('modifiedTime'),
                    is_cloud=True
                )
                card.noteClicked.connect(self.open_note.emit)
                self.cloud_list_layout.addWidget(card)
                
        self.cloud_list_layout.addStretch()

    def update_recent_list(self, recent_files, skip_store=False):
        """Update local notes display"""
        if not skip_store:
            self._local_notes = recent_files or []
            
        # Clear layout
        while self.local_list_layout.count():
            item = self.local_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        notes = self._filter_and_sort(self._local_notes, is_cloud=False)
        
        # Update count badge
        if self.local_count_badge:
            self.local_count_badge.setText(str(len(notes)))
            
        if not notes:
            empty = QLabel("No local notes yet. Create your first note!")
            empty.setObjectName("EmptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.local_list_layout.addWidget(empty)
        else:
            for path in notes:
                name = str(path).replace("\\", "/").split('/')[-1]
                preview = self._get_file_preview(path)
                modified = self._get_file_modified_time(path)
                
                card = NoteCard(
                    title=name,
                    path=path,
                    preview=preview,
                    modified_time=modified,
                    is_cloud=False
                )
                card.noteClicked.connect(self.open_note.emit)
                card.deleteRequested.connect(self.delete_note)
                self.local_list_layout.addWidget(card)
                
        self.local_list_layout.addStretch()

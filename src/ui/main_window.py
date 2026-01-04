"""
Glassnotes Main Window
Premium glassmorphism window with status bar, settings integration, and polished UX
"""
import sys
import os
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QFont
from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QWidget, QFileDialog,
                              QHBoxLayout, QLabel, QFrame, QStatusBar)

from qfluentwidgets import (MSFluentWindow, NavigationItemPosition, FluentIcon as FIF,
                             TabWidget, setTheme, Theme, InfoBar, InfoBarPosition, 
                             setThemeColor, NavigationAvatarWidget, TransparentToolButton)

from src.ui.editor import Editor
from src.ui.hub import HubView
from src.ui.settings import SettingsView
from src.ui.styles import get_main_window_style, GlassColors
from src.logic.config import config
from src.logic.file_manager import file_manager
from src.logic.drive_service import drive_service


class StatusBarWidget(QWidget):
    """Custom status bar with editor statistics"""
    save_requested = pyqtSignal()
    save_as_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()
    zoom_reset_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(10)
        
        # Stats & Cursor Block
        self.stats_label = QLabel("0 words  •  0 characters")
        self.stats_label.setStyleSheet(f"color: {GlassColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500;")
        
        self.cursor_label = QLabel("line 1, column 1")
        self.cursor_label.setStyleSheet(f"color: {GlassColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500;")
        
        info_block = self._create_block([self.stats_label, self.cursor_label])
        
        # Consistent spacing within the unified info block
        info_layout = info_block.layout()
        info_layout.setSpacing(24) # More breathing room between the two groups
        info_layout.setContentsMargins(14, 0, 14, 0)
        
        # Edit Block (Undo/Redo)
        self.undo_btn = TransparentToolButton(FIF.LEFT_ARROW)
        self.undo_btn.setFixedSize(28, 28)
        self.undo_btn.setIconSize(QSize(16, 16))
        self.undo_btn.setToolTip("Undo (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        
        self.redo_btn = TransparentToolButton(FIF.RIGHT_ARROW)
        self.redo_btn.setFixedSize(28, 28)
        self.redo_btn.setIconSize(QSize(16, 16))
        self.redo_btn.setToolTip("Redo (Ctrl+Y)")
        self.redo_btn.clicked.connect(self.redo_requested.emit)
        
        edit_block = self._create_block([self.undo_btn, self.redo_btn])
        
        # Zoom Block
        self.zoom_out_btn = TransparentToolButton(FIF.ZOOM_OUT)
        self.zoom_out_btn.setFixedSize(28, 28)
        self.zoom_out_btn.setIconSize(QSize(16, 16))
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.clicked.connect(self.zoom_out_requested.emit)
        
        self.zoom_reset_btn = TransparentToolButton(FIF.SYNC)
        self.zoom_reset_btn.setFixedSize(28, 28)
        self.zoom_reset_btn.setIconSize(QSize(16, 16))
        self.zoom_reset_btn.setToolTip("Reset Zoom (Ctrl+0)")
        self.zoom_reset_btn.clicked.connect(self.zoom_reset_requested.emit)
        
        self.zoom_in_btn = TransparentToolButton(FIF.ZOOM_IN)
        self.zoom_in_btn.setFixedSize(28, 28)
        self.zoom_in_btn.setIconSize(QSize(16, 16))
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl+=)")
        self.zoom_in_btn.clicked.connect(self.zoom_in_requested.emit)
        
        zoom_block = self._create_block([self.zoom_out_btn, self.zoom_reset_btn, self.zoom_in_btn])
        
        # Save Block
        self.save_label = QLabel("✓ Saved")
        self.save_label.setStyleSheet(f"color: {GlassColors.SUCCESS}; font-size: 11px; font-weight: 500;")
        
        self.save_btn = TransparentToolButton(FIF.SAVE)
        self.save_btn.setFixedSize(28, 28)
        self.save_btn.setIconSize(QSize(16, 16))
        self.save_btn.setToolTip("Save Note (Ctrl+S)")
        self.save_btn.clicked.connect(self.save_requested.emit)
        
        self.save_as_btn = TransparentToolButton(FIF.SAVE_AS)
        self.save_as_btn.setFixedSize(28, 28)
        self.save_as_btn.setIconSize(QSize(16, 16))
        self.save_as_btn.setToolTip("Save As... (Ctrl+Shift+S)")
        self.save_as_btn.clicked.connect(self.save_as_requested.emit)
        
        save_block = self._create_block([self.save_label, self.save_btn, self.save_as_btn])
        
        # Assemble Layout
        layout.addWidget(info_block)
        layout.addStretch()
        layout.addWidget(edit_block)
        layout.addWidget(zoom_block)
        layout.addWidget(save_block)
        
    def _create_block(self, widgets):
        """Create a styled visual block containing widgets"""
        frame = QFrame()
        frame.setFixedHeight(34) # slightly larger than buttons
        frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid {GlassColors.GLASS_BORDER};
                border-radius: 6px;
                padding: 0px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)
        
        for w in widgets:
            layout.addWidget(w)
            
        return frame
        
    def update_counts(self, words, characters):
        """Update word and character counts"""
        self.stats_label.setText(f"{words:,} words  •  {characters:,} characters")
        
    def update_cursor(self, line, column):
        """Update cursor position display"""
        self.cursor_label.setText(f"line {line}, column {column}")
        
    def set_modified(self, modified=True):
        """Update save status indicator"""
        if modified:
            self.save_label.setText("● Modified")
            self.save_label.setStyleSheet(f"color: {GlassColors.WARNING}; font-size: 11px; font-weight: 500;")
        else:
            self.save_label.setText("✓ Saved")
            self.save_label.setStyleSheet(f"color: {GlassColors.SUCCESS}; font-size: 11px; font-weight: 500;")


class MainWindow(MSFluentWindow):
    """Premium glassmorphism main window"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.setWindowTitle("Glassnotes")
        self.setWindowIcon(QIcon(config.get_resource_path("assets/icon.ico")))
        width = config.get("window_width", 1280)
        height = config.get("window_height", 720)
        self.resize(width, height)
        self.setMinimumSize(900, 600)
        self.setAcceptDrops(True) # Enable Drag & Drop
        self._center_window()
        
        # Theme setup
        setTheme(Theme.DARK)
        accent_color = config.settings.get("accent_color", "#9D46FF")
        setThemeColor(accent_color)
        
        # Apply premium styling
        self.setStyleSheet(get_main_window_style())
        
        # Initialize components
        # Initialize components
        self._init_components()
        self._init_navigation()
        self._init_shortcuts()
        self._init_status_bar()
        self._connect_settings_signals()
        
        # Initial data and session restoration
        self.update_hub_data()
        self._restore_session()
        
    def _center_window(self):
        """Center the window on the primary screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def _connect_settings_signals(self):
        """Connect settings changes to application updates"""
        self.settings.font_size_changed.connect(self._update_all_editors_font)
        self.settings.accent_changed.connect(self._update_application_accent)
        self.settings.login_successful.connect(self.refresh_cloud_list)
        self.settings.logout_requested.connect(self._on_logout)
        
    def _update_all_editors_font(self, size):
        """Update font size for all open tabs"""
        target_size = max(1, int(size))
            
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, Editor):
                font = editor.font()
                font.setPointSize(target_size)
                editor.setFont(font)
                
    def _update_application_accent(self, color):
        """Update application-wide accent color"""
        setThemeColor(color)
        # Update theme color (handled by qfluentwidgets)
        # But we also need to trigger editor updates for custom painting
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, Editor):
                editor._highlight_current_line()
                
        
    def _init_components(self):
        """Initialize all UI components"""
        
        # Tab widget for editors
        self.tabs = TabWidget()
        self.tabs.setObjectName("EditorTabs")
        self.tabs.setTabMaximumWidth(220)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabAddRequested.connect(lambda: self.add_new_tab())
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Container for tabs to accommodate status bar
        self.tabs_container = QWidget()
        self.tabs_container.setObjectName("EditorTabsContainer")
        container_layout = QVBoxLayout(self.tabs_container)
        container_layout.setContentsMargins(0, 0, 0, 48) # Reserve space for status bar
        container_layout.setSpacing(0)
        container_layout.addWidget(self.tabs)
        
        # Hub view
        self.hub = HubView()
        self.hub.new_note.connect(lambda: self.add_new_tab())
        self.hub.open_note.connect(self.open_file_path)
        self.hub.refresh_requested.connect(self.update_hub_data)
        self.hub.open_file_requested.connect(self.open_file_dialog)
        self.hub.login_btn.clicked.connect(self.login_google)
        
        # Settings view
        self.settings = SettingsView()
        self.settings.font_size_changed.connect(self._on_font_size_changed)
        self.settings.logout_requested.connect(self._on_logout)
        
    def _init_navigation(self):
        """Setup navigation sidebar"""
        # Main navigation items
        self.addSubInterface(self.hub, FIF.HOME, "Home")
        self.addSubInterface(self.tabs_container, FIF.EDIT, "Editor")
        
        # Bottom navigation items
        self.addSubInterface(
            self.settings, FIF.SETTING, "Settings",
            position=NavigationItemPosition.BOTTOM
        )
        
        # Set initial view
        self.navigationInterface.setCurrentItem(self.hub.objectName())
        
    def _init_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Save: Ctrl+S
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_current_note)
        
        # Save As: Ctrl+Shift+S
        self.save_as_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.save_as_shortcut.activated.connect(self.save_as_current_note)
        
        # New: Ctrl+N or Ctrl+T
        self.new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_shortcut.activated.connect(lambda: self.add_new_tab())
        
        self.new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.new_tab_shortcut.activated.connect(lambda: self.add_new_tab())
        
        # Open: Ctrl+O
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.open_shortcut.activated.connect(self.open_file_dialog)
        
        # Close Tab: Ctrl+W
        self.close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_shortcut.activated.connect(self._close_current_tab)
        
        # Undo: Ctrl+Z
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self._undo)
        
        # Redo: Ctrl+Y
        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redo_shortcut.activated.connect(self._redo)
        
        # Zoom In: Ctrl+= or Ctrl++
        self.zoom_in_equal_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.zoom_in_equal_shortcut.activated.connect(self._zoom_in)
        
        self.zoom_in_plus_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_plus_shortcut.activated.connect(self._zoom_in)
        
        # Zoom Out: Ctrl+-
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self._zoom_out)
        
        # Reset Zoom: Ctrl+0
        self.zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        self.zoom_reset_shortcut.activated.connect(self._reset_zoom)
        
    def _init_status_bar(self):
        """Setup custom status bar"""
        self.status_widget = StatusBarWidget()
        self.status_widget.save_requested.connect(self.save_current_note)
        self.status_widget.save_as_requested.connect(self.save_as_current_note)
        self.status_widget.undo_requested.connect(self._undo)
        self.status_widget.redo_requested.connect(self._redo)
        self.status_widget.zoom_in_requested.connect(self._zoom_in)
        self.status_widget.zoom_out_requested.connect(self._zoom_out)
        self.status_widget.zoom_reset_requested.connect(self._reset_zoom)
        
        # Create status bar container at window level
        # Create status bar container at window level
        self.status_bar_frame = QFrame()
        self.status_bar_frame.setFixedHeight(48)
        self.status_bar_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(15, 10, 25, 0.98);
                border-top: 1px solid {GlassColors.GLASS_BORDER};
                margin: 0px;
                border-radius: 0px;
            }}
        """)
        
        status_layout = QHBoxLayout(self.status_bar_frame)
        status_layout.setContentsMargins(12, 0, 12, 0) # Less vertical padding
        status_layout.addWidget(self.status_widget)
        
        # Add to main layout (bottom of window)
        # To make it full width at the bottom, we move it to the window level
        self.status_bar_frame.setParent(self)
        
        # Hide by default (starts on Hub)
        self.status_bar_frame.hide()
        
        # Increase status bar height to fit blocks
        self.status_bar_frame.setFixedHeight(48)
        
        # Connect view changes to toggle visibility
        self.stackedWidget.currentChanged.connect(self._on_view_changed)
            
    def resizeEvent(self, event):
        """Handle resize to keep status bar at the bottom and aligned with content"""
        super().resizeEvent(event)
        if hasattr(self, 'status_bar_frame') and hasattr(self, 'navigationInterface'):
            # Offsets the status bar to start after the navigation sidebar
            nav_width = self.navigationInterface.width()
            bar_width = self.width() - nav_width
            self.status_bar_frame.setGeometry(
                nav_width, 
                self.height() - 48, 
                bar_width, 
                48
            )
            self.status_bar_frame.raise_()

    def dragEnterEvent(self, event):
        """Handle drag enter for file dropping"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle dropping of files"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            # Check for valid text extensions or try to open
            if f and os.path.exists(f):
                # Basic check for text-like extensions, but we can try opening anything
                # or let open_file_path handle it.
                # Ideally, we only accept text/code files.
                valid_exts = ('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml')
                if f.lower().endswith(valid_exts) or os.path.getsize(f) < 1000000: # Allow small files regardless of ext
                    self.open_file_path(f)
                    

    def _on_view_changed(self, index):
        """Toggle status bar visibility based on current view"""
        widget = self.stackedWidget.widget(index)
        if widget == self.tabs_container:
            self.status_bar_frame.show()
        else:
            self.status_bar_frame.hide()
        self._save_session()

    def _on_tab_changed(self, index):
        """Handle tab selection change"""
        if index >= 0:
            editor = self.tabs.widget(index)
            if editor and isinstance(editor, Editor):
                # Connect signals for status bar updates
                try:
                    editor.word_count_changed.disconnect()
                except:
                    pass
                try:
                    editor.cursor_position_changed.disconnect()
                except:
                    pass
                    
                editor.word_count_changed.connect(self.status_widget.update_counts)
                editor.cursor_position_changed.connect(self.status_widget.update_cursor)
                
                # Trigger initial update
                content = editor.get_content()
                words = len(content.split()) if content.strip() else 0
                chars = len(content)
                self.status_widget.update_counts(words, chars)
                
                cursor = editor.textCursor()
                self.status_widget.update_cursor(
                    cursor.blockNumber() + 1,
                    cursor.columnNumber() + 1
                )
                self._save_session()
                
    def _on_font_size_changed(self, size):
        """Apply font size change to all editors"""
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, Editor):
                editor.set_font_size(size)
                
    def _on_logout(self):
        """Handle Google Drive logout"""
        drive_service.logout()
        
        # Update hub
        self.hub.update_cloud_list([])
        self.update_hub_data()
        
        InfoBar.success(
            "Disconnected",
            "Google Drive has been disconnected",
            duration=3000,
            parent=self
        )
        
    def _zoom_in(self):
        """Zoom in current editor"""
        index = self.tabs.currentIndex()
        if index >= 0:
            editor = self.tabs.widget(index)
            if isinstance(editor, Editor):
                editor.zoom_in()
                
    def _zoom_out(self):
        """Zoom out current editor"""
        index = self.tabs.currentIndex()
        if index >= 0:
            editor = self.tabs.widget(index)
            if isinstance(editor, Editor):
                editor.zoom_out()
                
    def _undo(self):
        """Undo last action in current editor"""
        index = self.tabs.currentIndex()
        if index >= 0:
            editor = self.tabs.widget(index)
            if isinstance(editor, Editor):
                editor.undo()

    def _redo(self):
        """Redo last action in current editor"""
        index = self.tabs.currentIndex()
        if index >= 0:
            editor = self.tabs.widget(index)
            if isinstance(editor, Editor):
                editor.redo()
                
    def _reset_zoom(self):
        """Reset zoom to default size"""
        default_size = config.settings.get("font_size", 13)
        index = self.tabs.currentIndex()
        if index >= 0:
            editor = self.tabs.widget(index)
            if isinstance(editor, Editor):
                editor.set_font_size(default_size)
                
    def _close_current_tab(self):
        """Close the current tab"""
        index = self.tabs.currentIndex()
        if index >= 0:
            self.close_tab(index)
    
    def _save_session(self):
        """Save current open tabs to session"""
        session_tabs = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if not isinstance(editor, Editor):
                continue
                
            name = self.tabs.tabText(i)
            path = editor.file_path
            drive_id = editor.drive_id
            
            # If unsaved, create a backup
            is_backup = False
            if not path and not drive_id:
                backup_path = config.BACKUP_DIR / f"tab_{i}.txt"
                content = editor.get_content()
                if content.strip():
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    path = str(backup_path)
                    is_backup = True
            
            session_tabs.append({
                "name": name,
                "path": str(path) if path else None,
                "drive_id": drive_id,
                "is_backup": is_backup
            })
            
        config.set("session_tabs", session_tabs)

    def _restore_session(self):
        """Restore tabs from previous session"""
        session_tabs = config.get("session_tabs", [])
        if not session_tabs:
            return
            
        for tab in session_tabs:
            path = tab.get("path")
            drive_id = tab.get("drive_id")
            name = tab.get("name", "Untitled")
            is_backup = tab.get("is_backup", False)
            
            if is_backup and path and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.add_new_tab(name, content)
                # After restoring backup, delete it so it doesn't linger 
                # if not closed properly next time (it will be recreated on next save_session)
                try: os.remove(path)
                except: pass
            elif path and os.path.exists(path):
                self.open_file_path(path)
            elif drive_id:
                self.add_new_tab(name, "", drive_id=drive_id)
                # Note: Content will be fetchable via Drive if needed, 
                # but for now we just restore the tab reference

        # Reset selection to first tab if any exist
        if self.tabs.count() > 0:
            self.tabs.setCurrentIndex(0)
            self.switchTo(self.tabs_container)

    def update_hub_data(self):
        """Refresh hub with current data"""
        # Get all local files from notes dir
        local_files = file_manager.list_files(config.NOTES_DIR)
        
        # Merge with recent files (preserving order but avoiding duplicates)
        recent_files = config.settings.get("recent_files", [])
        
        # Valid recent files
        valid_recents = []
        seen_paths = set()
        
        # First add valid recent files (preserving user order)
        for f in recent_files:
            if os.path.exists(f):
                norm_path = os.path.normpath(f)
                valid_recents.append(f)
                seen_paths.add(norm_path)
        
        # Then add any missing files from notes directory
        for f in local_files:
            norm_path = os.path.normpath(f)
            if norm_path not in seen_paths:
                valid_recents.append(f)
                
        self.hub.update_recent_list(valid_recents)
        
        if config.settings.get("google_logged_in"):
            self.refresh_cloud_list()
        else:
            self.hub.update_cloud_list([])

    def refresh_cloud_list(self):
        """Fetch and display cloud notes"""
        try:
            drive_notes = drive_service.list_notes()
            self.hub.update_cloud_list(drive_notes)
            self.settings.update_cloud_status(True)
        except Exception as e:
            print(f"Failed to refresh cloud list: {e}")
            self.settings.update_cloud_status(False)

    def login_google(self):
        """Initiate Google Drive authentication"""
        try:
            if drive_service.authenticate():
                InfoBar.success(
                    "Connected",
                    "Successfully connected to Google Drive",
                    duration=3000,
                    parent=self
                )
                self.refresh_cloud_list()
                self.settings.update_cloud_status(True)
        except FileNotFoundError:
            InfoBar.error(
                "Credentials Missing",
                "Please place 'credentials.json' in the project root or the app data folder.",
                duration=5000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                "Connection Failed",
                str(e),
                duration=5000,
                parent=self
            )

    def add_new_tab(self, name="Untitled", content="", path=None, drive_id=None):
        """Create a new editor tab"""
        editor = Editor(content)
        editor.file_path = path
        editor.drive_id = drive_id
        
        # Connect editor signals for status bar updates
        editor.textChanged.connect(lambda: self.status_widget.set_modified(True))
        editor.textChanged.connect(self._save_session) # Auto-save session on changes
        editor.word_count_changed.connect(self.status_widget.update_counts)
        editor.cursor_position_changed.connect(self.status_widget.update_cursor)
        
        index = self.tabs.addTab(editor, name)
        self.tabs.setCurrentIndex(index)
        self.switchTo(self.tabs_container)
        
        # Initial status - trigger count update
        text = editor.get_content()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        self.status_widget.update_counts(words, chars)
        
        cursor = editor.textCursor()
        self.status_widget.update_cursor(
            cursor.blockNumber() + 1,
            cursor.columnNumber() + 1
        )
        self.status_widget.set_modified(False)
        
    def open_file_dialog(self):
        """Open file picker dialog"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Note",
            str(config.NOTES_DIR),
            "Supported Files (*.txt *.md *.py *.js *.html *.css *.json *.xml *.yaml *.yml *.ini *.log);;All Files (*)"
        )
        if path:
            self.open_file_path(path)

    def open_file_path(self, path_or_id):
        """Open a note by path or Drive ID"""
        if os.path.exists(path_or_id):
            # Local file
            content = file_manager.read_file(path_or_id)
            if content is not None:
                name = os.path.basename(path_or_id)
                self.add_new_tab(name, content, path=path_or_id)
                config.add_recent_file(path_or_id)
                self.update_hub_data()
        else:
            # Assume Drive ID
            try:
                content = drive_service.download_note(path_or_id)
                name = "Cloud Note"
                
                notes = drive_service.list_notes()
                if notes:
                    for note in notes:
                        if note['id'] == path_or_id:
                            name = note['name']
                            break
                            
                self.add_new_tab(name, content, drive_id=path_or_id)
            except Exception as e:
                InfoBar.error(
                    "Error",
                    f"Failed to download cloud note: {e}",
                    parent=self
                )

    def save_current_note(self):
        """Save the current note"""
        index = self.tabs.currentIndex()
        if index == -1:
            return
            
        editor = self.tabs.widget(index)
        if not editor or not isinstance(editor, Editor):
            return
            
        content = editor.get_content()
        name = self.tabs.tabText(index)
        
        # Cloud save
        if hasattr(editor, 'drive_id') and editor.drive_id:
            try:
                drive_service.upload_note(name, content, editor.drive_id)
                InfoBar.success(
                    "Cloud Saved",
                    "Note updated in Google Drive",
                    duration=2000,
                    parent=self
                )
                self.status_widget.set_modified(False)
                return
            except Exception as e:
                InfoBar.error(
                    "Cloud Save Failed",
                    str(e),
                    parent=self
                )

        # Local save
        if not hasattr(editor, 'file_path') or editor.file_path is None:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Note",
                str(config.NOTES_DIR),
                "Text Files (*.txt);;Markdown (*.md);;All Files (*)"
            )
            if path:
                editor.file_path = path
                self.tabs.setTabText(index, os.path.basename(path))
            else:
                return

        if file_manager.save_file(editor.file_path, content):
            config.add_recent_file(editor.file_path)
            self.update_hub_data()
            self.status_widget.set_modified(False)
            InfoBar.success(
                "Saved",
                "Note saved successfully",
                duration=2000,
                parent=self
            )

    def save_as_current_note(self):
        """Save the current note with a new path"""
        index = self.tabs.currentIndex()
        if index == -1:
            return
            
        editor = self.tabs.widget(index)
        if not editor or not isinstance(editor, Editor):
            return
            
        # Store old path
        old_path = getattr(editor, 'file_path', None)
        old_drive_id = getattr(editor, 'drive_id', None)
        
        # Clear paths to force Save As dialog
        editor.file_path = None
        editor.drive_id = None
        
        # Trigger save
        self.save_current_note()
        
        # Check if saved to a new location
        new_path = getattr(editor, 'file_path', None)
        new_drive_id = getattr(editor, 'drive_id', None)

        # If save was successful (has a new path/id) and it's different from before
        if (new_path or new_drive_id) and (new_path != old_path or new_drive_id != old_drive_id):
            # Delete old local file if it existed
            if old_path and os.path.exists(old_path):
                from src.logic.file_manager import file_manager
                file_manager.delete_file(old_path)
                config.remove_recent_file(old_path)
            
            # Update hub
            self.update_hub_data()
        
        # If save was cancelled (still no path), restore old path
        elif editor.file_path is None and editor.drive_id is None:
            editor.file_path = old_path
            editor.drive_id = old_drive_id

    def close_tab(self, index):
        """Close a tab by index"""
        editor = self.tabs.widget(index)
        if isinstance(editor, Editor) and editor.file_path:
            # If it was a backup file, we can optionally clean it up, 
            # though _save_session handles current state.
            pass
            
        self.tabs.removeTab(index)
        self._save_session()
        
        if self.tabs.count() == 0:
            self.switchTo(self.hub)
            self.status_widget.set_modified(False)

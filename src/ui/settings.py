"""
Glassnotes Settings Panel
Premium glassmorphism settings interface with appearance and editor customization
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QFrame, QScrollArea, QSpacerItem, QSizePolicy, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from qfluentwidgets import (SubtitleLabel, BodyLabel, ComboBox, ToolButton,
                             SwitchButton, PrimaryPushButton, PushButton,
                             FluentIcon as FIF, CardWidget, setThemeColor)

from src.ui.styles import get_settings_style, GlassColors
from src.logic.config import config
from src.logic.drive_service import drive_service


class GlassNumberPicker(QWidget):
    """Custom high-visibility number selector with glassmorphism styling"""
    valueChanged = pyqtSignal(int)

    def __init__(self, value, min_v, max_v, suffix="", parent=None):
        super().__init__(parent)
        self.value = value
        self.min_v = min_v
        self.max_v = max_v
        self.suffix = suffix

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Value Input (Editable SpinBox with hidden buttons)
        self.input = QSpinBox()
        self.input.setRange(min_v, max_v)
        self.input.setValue(value)
        self.input.setSuffix(suffix)
        self.input.setFixedWidth(70)
        self.input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Style to look like a glass input and hide native buttons
        self.input.setStyleSheet(f"""
            QSpinBox {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid {GlassColors.GLASS_BORDER};
                border-radius: 6px;
                color: {GlassColors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
                padding: 4px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
                height: 0px;
                border: none;
            }}
        """)

        # Buttons container
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(2)
        
        self.btn_up = ToolButton(FIF.UP, self)
        self.btn_down = ToolButton(FIF.DOWN, self)

        for btn in [self.btn_up, self.btn_down]:
            btn.setFixedSize(32, 22)
            btn.setStyleSheet(f"""
                ToolButton {{
                    background: rgba(157, 70, 255, 0.15);
                    border: 1px solid rgba(157, 70, 255, 0.2);
                    border-radius: 4px;
                }}
                ToolButton:hover {{
                    background: rgba(157, 70, 255, 0.4);
                }}
            """)

        # Connect signals
        self.btn_up.clicked.connect(self.input.stepUp)
        self.btn_down.clicked.connect(self.input.stepDown)
        self.input.valueChanged.connect(self.valueChanged.emit)

        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)

        layout.addWidget(self.input)
        layout.addLayout(btn_layout)

    def setValue(self, value):
        self.input.setValue(value)


class SettingsSection(CardWidget):
    """A collapsible settings section card"""
    
    def __init__(self, title, icon="", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsSection")
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 20)
        self._layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(12)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 20px; background: transparent;")
            header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.DemiBold))
        title_label.setStyleSheet(f"color: {GlassColors.TEXT_PRIMARY}; background: transparent;")
        header.addWidget(title_label)
        header.addStretch()
        
        self._layout.addLayout(header)
        
        # Content container
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(16)
        self._layout.addLayout(self.content_layout)
        
    def add_setting(self, widget):
        """Add a setting row to the section"""
        self.content_layout.addWidget(widget)


class SettingRow(QWidget):
    """A single setting row with label, description, and control"""
    
    def __init__(self, label, description="", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(20)
        
        # Label and description
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.label = QLabel(label)
        self.label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.label.setStyleSheet(f"color: {GlassColors.TEXT_PRIMARY}; background: transparent;")
        text_layout.addWidget(self.label)
        
        if description:
            self.desc = QLabel(description)
            self.desc.setFont(QFont("Segoe UI", 11))
            self.desc.setStyleSheet(f"color: {GlassColors.TEXT_TERTIARY}; background: transparent;")
            self.desc.setWordWrap(True)
            text_layout.addWidget(self.desc)
            
        layout.addLayout(text_layout, 1)
        
        # Control container
        self.control_container = QHBoxLayout()
        self.control_container.setSpacing(8)
        layout.addLayout(self.control_container)
        
    def add_control(self, widget):
        """Add a control widget"""
        self.control_container.addWidget(widget)


class SettingsView(QWidget):
    """Premium glassmorphism settings panel"""
    
    # Signals
    theme_changed = pyqtSignal(str)
    accent_changed = pyqtSignal(str)
    font_size_changed = pyqtSignal(int)
    login_successful = pyqtSignal()
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsView")
        self._setup_ui()
        self._load_settings()
    def _setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 40, 48, 40)
        layout.setSpacing(24)
        
        # Apply styling
        self.setStyleSheet(get_settings_style())
        
        # Header
        header = QLabel("⚙️ Settings")
        header.setObjectName("SettingsTitle")
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {GlassColors.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(header)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 16, 0)
        scroll_layout.setSpacing(20)
        
        # === APPEARANCE SECTION ===
        appearance = SettingsSection("Appearance", "🎨")
        appearance.setStyleSheet(f"""
            #SettingsSection {{
                background: rgba(35, 25, 55, 0.6);
                border: 1px solid {GlassColors.GLASS_BORDER};
                border-radius: 16px;
            }}
        """)
        
        # Accent Color
        accent_row = SettingRow("Accent Color", "Primary color used throughout the app")
        self.accent_combo = ComboBox()
        self.accent_combo.addItems(["Purple", "Blue", "Pink", "Teal", "Orange"])
        self.accent_combo.setFixedWidth(140)
        self.accent_combo.currentTextChanged.connect(self._on_accent_changed)
        accent_row.add_control(self.accent_combo)
        appearance.add_setting(accent_row)
        
        scroll_layout.addWidget(appearance)
        
        # === EDITOR SECTION ===
        editor = SettingsSection("Editor", "📝")
        editor.setStyleSheet(f"""
            #SettingsSection {{
                background: rgba(35, 25, 55, 0.6);
                border: 1px solid {GlassColors.GLASS_BORDER};
                border-radius: 16px;
            }}
        """)
        
        # Font Size
        font_row = SettingRow("Font Size", "Editor text size (8-24 pt)")
        self.font_picker = GlassNumberPicker(
            config.settings.get("font_size", 13), 8, 24, " pt"
        )
        self.font_picker.valueChanged.connect(self._on_font_size_changed)
        font_row.add_control(self.font_picker)
        editor.add_setting(font_row)
        
        # Word Wrap
        wrap_row = SettingRow("Word Wrap", "Wrap long lines at window edge")
        self.wrap_switch = SwitchButton()
        self.wrap_switch.setChecked(config.settings.get("word_wrap", True))
        wrap_row.add_control(self.wrap_switch)
        editor.add_setting(wrap_row)
        
        # Line Numbers
        lines_row = SettingRow("Line Numbers", "Show line numbers in editor")
        self.lines_switch = SwitchButton()
        self.lines_switch.setChecked(config.settings.get("show_line_numbers", True))
        lines_row.add_control(self.lines_switch)
        editor.add_setting(lines_row)
        
        scroll_layout.addWidget(editor)
        
        # === CLOUD SECTION ===
        cloud = SettingsSection("Cloud Storage", "☁️")
        cloud.setStyleSheet(f"""
            #SettingsSection {{
                background: rgba(35, 25, 55, 0.6);
                border: 1px solid {GlassColors.GLASS_BORDER};
                border-radius: 16px;
            }}
        """)
        
        status_row = SettingRow("Google Drive", "Sync notes with your Google account")
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet(f"color: {GlassColors.TEXT_TERTIARY}; background: transparent;")
        
        self.login_btn = PrimaryPushButton("Connect")
        self.login_btn.clicked.connect(self._on_login)
        
        self.logout_btn = PushButton("Disconnect")
        self.logout_btn.setEnabled(False)
        self.logout_btn.clicked.connect(self._on_logout)
        
        status_row.add_control(self.status_label)
        status_row.add_control(self.login_btn)
        status_row.add_control(self.logout_btn)
        cloud.add_setting(status_row)
        
        # scroll_layout.addWidget(cloud)
        
        # === ABOUT SECTION ===
        about = SettingsSection("About", "ℹ️")
        about.setStyleSheet(f"""
            #SettingsSection {{
                background: rgba(35, 25, 55, 0.6);
                border: 1px solid {GlassColors.GLASS_BORDER};
                border-radius: 16px;
            }}
        """)
        
        # Version info
        version_label = QLabel("Glassnotes v1.0.0")
        version_label.setStyleSheet(f"color: {GlassColors.TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        about.content_layout.addWidget(version_label)
        
        desc_label = QLabel("A beautiful, modern note-taking app with glassmorphism design.")
        desc_label.setStyleSheet(f"color: {GlassColors.TEXT_TERTIARY}; font-size: 12px; background: transparent;")
        desc_label.setWordWrap(True)
        about.content_layout.addWidget(desc_label)
        
        scroll_layout.addWidget(about)
        
        # Spacer
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)
        
    def _load_settings(self):
        """Load current settings into controls"""
        # Accent color
        current_accent = config.settings.get("accent_color", "#9D46FF")
        color_map = {
            "#9D46FF": "Purple",
            "#3B82F6": "Blue",
            "#EC4899": "Pink",
            "#14B8A6": "Teal",
            "#F97316": "Orange"
        }
        if current_accent in color_map:
            self.accent_combo.setCurrentText(color_map[current_accent])

        # Font size
        self.font_picker.setValue(config.settings.get("font_size", 13))

        # Word wrap
        self.wrap_switch.setChecked(config.settings.get("word_wrap", True))
        
        # Line numbers
        self.lines_switch.setChecked(config.settings.get("show_line_numbers", True))
        
        # Google status
        is_connected = config.settings.get("google_logged_in", False)
        self.update_cloud_status(is_connected)
        
    def _on_accent_changed(self, color_name):
        """Handle accent color change"""
        color_map = {
            "Purple": "#9D46FF",
            "Blue": "#3B82F6",
            "Pink": "#EC4899",
            "Teal": "#14B8A6",
            "Orange": "#F97316"
        }
        if color_name in color_map:
            setThemeColor(color_map[color_name])
            config.settings["accent_color"] = color_map[color_name]
            config.save()
            self.accent_changed.emit(color_map[color_name])
            
    def _on_font_size_changed(self, value):
        """Handle font size change"""
        config.settings["font_size"] = value
        config.save()
        self.font_size_changed.emit(value)
        
    def _on_login(self):
        """Handle login button click"""
        try:
            if drive_service.authenticate():
                self.update_cloud_status(True)
                self.login_successful.emit()
                QMessageBox.information(self, "Success", "Successfully connected to Google Drive!")
        except FileNotFoundError as e:
            QMessageBox.critical(
                self, "Error", 
                f"{str(e)}\n\nPlease ensure 'credentials.json' is available to enable Google integration."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")

    def _on_logout(self):
        """Handle logout button click"""
        drive_service.logout()
        self.update_cloud_status(False)
        self.logout_requested.emit()
        
    def update_cloud_status(self, connected):
        """Update cloud connection status display"""
        try:
            if connected:
                self.status_label.setText("Connected")
                self.status_label.setStyleSheet(f"color: {GlassColors.SUCCESS}; background: transparent;")
                self.login_btn.hide()
                self.logout_btn.show()
                self.logout_btn.setEnabled(True)
            else:
                self.status_label.setText("Not connected")
                self.status_label.setStyleSheet(f"color: {GlassColors.TEXT_TERTIARY}; background: transparent;")
                self.login_btn.show()
                self.logout_btn.hide()
                self.logout_btn.setEnabled(False)
        except RuntimeError:
            pass  # Widget might be deleted

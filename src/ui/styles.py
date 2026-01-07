"""
Glassnotes Premium Theme System
Centralized styling for consistent premium glassmorphism aesthetics
"""


class GlassColors:
    """Premium color palette for glassmorphism design"""

    # Primary accent colors
    PRIMARY = "#9D46FF"
    PRIMARY_LIGHT = "#B76EFF"
    PRIMARY_DARK = "#7B35CC"
    PRIMARY_GLOW = "rgba(157, 70, 255, 0.4)"

    # Background gradient stops
    BG_DARK_1 = "#0a0612"
    BG_DARK_2 = "#12081f"
    BG_DARK_3 = "#1a0f2e"
    BG_ACCENT = "#0f0a1a"

    # Glass surface colors
    GLASS_BG = "rgba(25, 18, 40, 0.85)"
    GLASS_BG_HOVER = "rgba(40, 28, 65, 0.9)"
    GLASS_BORDER = "rgba(157, 70, 255, 0.15)"
    GLASS_BORDER_HOVER = "rgba(157, 70, 255, 0.4)"
    GLASS_BORDER_ACTIVE = "rgba(157, 70, 255, 0.6)"

    # Text hierarchy
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "rgba(255, 255, 255, 0.75)"
    TEXT_TERTIARY = "rgba(255, 255, 255, 0.5)"
    TEXT_MUTED = "rgba(255, 255, 255, 0.35)"

    # Semantic colors
    SUCCESS = "#4ADE80"
    WARNING = "#FBBF24"
    ERROR = "#F87171"
    INFO = "#60A5FA"

    # Card colors
    CARD_BG = "rgba(35, 25, 55, 0.75)"
    CARD_BG_HOVER = "rgba(55, 40, 85, 0.85)"


class GlassEffects:
    """Glassmorphism effect constants"""

    BLUR_LIGHT = "10px"
    BLUR_MEDIUM = "20px"
    BLUR_HEAVY = "30px"

    BORDER_RADIUS_SM = "8px"
    BORDER_RADIUS_MD = "12px"
    BORDER_RADIUS_LG = "16px"
    BORDER_RADIUS_XL = "24px"

    SHADOW_SUBTLE = "0 4px 16px rgba(0, 0, 0, 0.2)"
    SHADOW_MEDIUM = "0 8px 32px rgba(0, 0, 0, 0.3)"
    SHADOW_GLOW = "0 0 30px rgba(157, 70, 255, 0.3)"

    TRANSITION_FAST = "150ms"
    TRANSITION_NORMAL = "250ms"
    TRANSITION_SLOW = "400ms"


def get_main_window_style():
    """Premium glassmorphism stylesheet for main window"""
    return f"""
        /* Main Window - Deep Space Background */
        MainWindow, MSFluentWindow {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {GlassColors.BG_DARK_1},
                stop:0.3 {GlassColors.BG_DARK_2},
                stop:0.7 {GlassColors.BG_DARK_3},
                stop:1 {GlassColors.BG_ACCENT}
            );
        }}
        
        /* Navigation Pane - Frosted Glass */
        NavigationInterface {{
            background-color: rgba(15, 10, 26, 0.7);
            border-right: 1px solid {GlassColors.GLASS_BORDER};
        }}
        
        /* Navigation Items */
        NavigationPushButton {{
            background: transparent;
            border-radius: {GlassEffects.BORDER_RADIUS_SM};
            padding: 8px 12px;
            margin: 2px 8px;
        }}
        
        NavigationPushButton:hover {{
            background: rgba(157, 70, 255, 0.12);
        }}
        
        NavigationPushButton:pressed, NavigationPushButton:checked {{
            background: rgba(157, 70, 255, 0.2);
            border-left: 3px solid {GlassColors.PRIMARY};
        }}
        
        /* Content Areas - Premium Frosted Glass */
        QWidget#HubView {{
            background-color: {GlassColors.GLASS_BG};
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_LG};
            margin: 8px 8px 2px 8px;
        }}
        
        QWidget#EditorTabs {{
            background-color: rgba(20, 15, 35, 0.92);
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_LG};
            margin: 8px 8px 2px 8px;
        }}
        
        /* Tab Bar - Polished Glass Tabs */
        QTabWidget::pane {{
            border: none;
            background: transparent;
        }}
        
        TabBar {{
            background: transparent;
        }}
        
        TabBar::tab {{
            background: rgba(100, 70, 160, 0.1);
            color: {GlassColors.TEXT_SECONDARY};
            border: 1px solid rgba(157, 70, 255, 0.08);
            border-bottom: none;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            padding: 10px 28px;
            margin-right: 4px;
            min-width: 130px;
            font-size: 13px;
            font-weight: 500;
        }}
        
        TabBar::tab:selected {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(157, 70, 255, 0.3),
                stop:1 rgba(157, 70, 255, 0.15)
            );
            color: {GlassColors.TEXT_PRIMARY};
            border: 1px solid {GlassColors.GLASS_BORDER_ACTIVE};
            border-bottom: none;
        }}
        
        TabBar::tab:hover:!selected {{
            background: rgba(157, 70, 255, 0.15);
            color: {GlassColors.TEXT_PRIMARY};
        }}
        
        /* Close Button on Tabs */
        TabBar QToolButton {{
            background: transparent;
            border: none;
            border-radius: 4px;
            padding: 2px;
        }}
        
        TabBar QToolButton:hover {{
            background: rgba(248, 113, 113, 0.3);
        }}
        
        /* Buttons - Premium Style */
        PrimaryPushButton {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {GlassColors.PRIMARY},
                stop:1 {GlassColors.PRIMARY_DARK}
            );
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: {GlassEffects.BORDER_RADIUS_SM};
            color: white;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 13px;
        }}
        
        PrimaryPushButton:hover {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {GlassColors.PRIMARY_LIGHT},
                stop:1 {GlassColors.PRIMARY}
            );
        }}
        
        PrimaryPushButton:pressed {{
            background: {GlassColors.PRIMARY_DARK};
        }}
        
        /* Secondary Buttons */
        PushButton {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_SM};
            color: {GlassColors.TEXT_SECONDARY};
            padding: 8px 20px;
            font-weight: 500;
        }}
        
        PushButton:hover {{
            background: rgba(157, 70, 255, 0.1);
            border-color: {GlassColors.GLASS_BORDER_HOVER};
            color: {GlassColors.TEXT_PRIMARY};
        }}
        
        /* Scroll Areas */
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        
        QScrollBar:vertical {{
            background: rgba(255, 255, 255, 0.03);
            width: 8px;
            border-radius: 4px;
            margin: 4px 2px;
        }}
        
        QScrollBar::handle:vertical {{
            background: rgba(157, 70, 255, 0.3);
            border-radius: 4px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: rgba(157, 70, 255, 0.5);
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: rgba(255, 255, 255, 0.03);
            height: 8px;
            border-radius: 4px;
            margin: 2px 4px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: rgba(157, 70, 255, 0.3);
            border-radius: 4px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: rgba(157, 70, 255, 0.5);
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Line Edit / Search Box */
        LineEdit, QLineEdit {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_SM};
            color: {GlassColors.TEXT_PRIMARY};
            padding: 10px 16px;
            font-size: 13px;
            selection-background-color: {GlassColors.PRIMARY};
        }}
        
        LineEdit:focus, QLineEdit:focus {{
            border-color: {GlassColors.GLASS_BORDER_ACTIVE};
            background: rgba(255, 255, 255, 0.08);
        }}
        
        /* ComboBox / Dropdown */
        ComboBox {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_SM};
            color: {GlassColors.TEXT_PRIMARY};
            padding: 8px 16px;
        }}
        
        ComboBox:hover {{
            border-color: {GlassColors.GLASS_BORDER_HOVER};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background: rgba(10, 6, 18, 0.8);
            border-top: 1px solid {GlassColors.GLASS_BORDER};
            color: {GlassColors.TEXT_TERTIARY};
            font-size: 12px;
            padding: 4px 12px;
        }}
        
        /* InfoBar Notifications */
        InfoBar {{
            background: {GlassColors.GLASS_BG};
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_MD};
        }}
        
        /* Tooltips */
        QToolTip {{
            background: {GlassColors.GLASS_BG};
            border: 1px solid {GlassColors.GLASS_BORDER};
            color: {GlassColors.TEXT_PRIMARY};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 12px;
        }}
    """


def get_note_card_style():
    """Premium glassmorphism style for note cards"""
    return f"""
        NoteCard {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(45, 32, 70, 0.6),
                stop:1 rgba(30, 22, 50, 0.6)
            );
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_MD};
            padding: 0px;
        }}
        
        NoteCard:hover {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(65, 45, 95, 0.75),
                stop:1 rgba(45, 32, 70, 0.75)
            );
            border: 1px solid {GlassColors.GLASS_BORDER_HOVER};
        }}
    """


def get_editor_style():
    """Premium glassmorphism style for the editor"""
    return f"""
        #NoteEditor {{
            background-color: rgba(15, 12, 25, 0.95);
            border: none;
            border-radius: 8px;
            padding: 24px;
            color: {GlassColors.TEXT_PRIMARY};
            selection-background-color: rgba(157, 70, 255, 0.4);
            selection-color: {GlassColors.TEXT_PRIMARY};
        }}
        
        #LineNumbers {{
            background: rgba(20, 15, 35, 0.9);
            color: {GlassColors.TEXT_MUTED};
            border: none;
            border-right: 1px solid {GlassColors.GLASS_BORDER};
            padding-right: 12px;
            padding-left: 12px;
            font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
            font-size: 13px;
        }}
    """


def get_hub_style():
    """Premium glassmorphism style for the hub view"""
    return f"""
        #HubView {{
            background-color: {GlassColors.GLASS_BG};
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_LG};
            margin: 8px 8px 2px 8px;
        }}

        /* Section Headers */
        #SectionHeader {{
            background: transparent;
            font-size: 20px;
            font-weight: 600;
            color: {GlassColors.TEXT_PRIMARY};
            padding: 8px 0px;
        }}

        #SearchContainer {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(157, 70, 255, 0.12);
            border-radius: {GlassEffects.BORDER_RADIUS_MD};
            padding: 12px 20px;
        }}

        /* Welcome Title */
        #WelcomeTitle {{
            font-size: 36px;
            font-weight: 700;
            color: {GlassColors.TEXT_PRIMARY};
            background: transparent;
        }}

        /* Subtitle */
        #WelcomeSubtitle {{
            font-size: 14px;
            color: {GlassColors.TEXT_TERTIARY};
            background: transparent;
        }}

        /* Settings Card (used for note sections) */
        #SettingsSection {{
            background: transparent;
            margin-bottom: 24px;
        }}

        #SettingsCard {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(157, 70, 255, 0.12);
            border-radius: 12px;
        }}

        /* Badge / Count */
        #CountBadge {{
            background: rgba(157, 70, 255, 0.2);
            color: {GlassColors.PRIMARY_LIGHT};
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 600;
        }}

        /* Empty State */
        #EmptyState {{
            color: {GlassColors.TEXT_MUTED};
            font-size: 14px;
            padding: 40px;
        }}
    """


def get_settings_style():
    """Premium glassmorphism style for settings panel"""
    return f"""
        #SettingsView {{
            background-color: {GlassColors.GLASS_BG};
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_LG};
            margin: 8px 8px 2px 8px;
        }}
        
        #SettingsSection {{
            background: transparent;
            margin-bottom: 24px;
        }}
        
        #SectionHeader {{
            font-size: 20px;
            font-weight: 600;
            color: {GlassColors.TEXT_PRIMARY};
            background: transparent;
        }}
        
        #SettingsCard {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(157, 70, 255, 0.12);
            border-radius: 12px;
        }}
        
        #SettingsTitle {{
            font-size: 28px;
            font-weight: 700;
            color: {GlassColors.TEXT_PRIMARY};
            padding-bottom: 8px;
            background: transparent;
        }}
        
        #SettingLabel {{
            font-size: 14px;
            font-weight: 500;
            color: {GlassColors.TEXT_PRIMARY};
        }}
        
        #SettingDescription {{
            font-size: 12px;
            color: {GlassColors.TEXT_TERTIARY};
        }}
        
        /* Slider */
        Slider::groove:horizontal {{
            background: rgba(255, 255, 255, 0.1);
            height: 6px;
            border-radius: 3px;
        }}
        
        Slider::handle:horizontal {{
            background: {GlassColors.PRIMARY};
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }}
        
        Slider::handle:horizontal:hover {{
            background: {GlassColors.PRIMARY_LIGHT};
        }}
        
        Slider::sub-page:horizontal {{
            background: {GlassColors.PRIMARY};
            border-radius: 3px;
        }}
        
        /* Switch Toggle */
        SwitchButton {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        SwitchButton:checked {{
            background: {GlassColors.PRIMARY};
        }}
    """


def get_search_bar_style():
    """Premium glassmorphism style for search bar"""
    return f"""
        #SearchInput, SearchBar QLineEdit {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid {GlassColors.GLASS_BORDER};
            border-radius: {GlassEffects.BORDER_RADIUS_SM};
            color: {GlassColors.TEXT_PRIMARY};
            padding: 8px 14px;
            font-size: 13px;
            selection-background-color: {GlassColors.PRIMARY};
        }}
        
        #SearchInput:focus, SearchBar QLineEdit:focus {{
            border-color: {GlassColors.GLASS_BORDER_ACTIVE};
            background: rgba(255, 255, 255, 0.08);
        }}
        
        #SearchBar {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(30, 22, 50, 0.98),
                stop:1 rgba(20, 15, 35, 0.98)
            );
            border-top: 1px solid {GlassColors.GLASS_BORDER};
        }}
    """

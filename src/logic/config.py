"""
Glassnotes Configuration
Handles app settings, paths, and persistence
"""
import os
import json
from pathlib import Path


class Config:
    """Application configuration manager"""
    
    APP_NAME = "Glassnotes"
    APP_VERSION = "1.0.0"
    APP_DIR = Path(os.environ.get("USERPROFILE", Path.home())) / f".{APP_NAME.lower()}"
    CONFIG_FILE = APP_DIR / "config.json"
    NOTES_DIR = APP_DIR / "notes"
    BACKUP_DIR = APP_DIR / "backups"

    def __init__(self):
        self._ensure_dirs()
        self.settings = self._load()

    def _ensure_dirs(self):
        """Create necessary directories"""
        self.APP_DIR.mkdir(exist_ok=True)
        self.NOTES_DIR.mkdir(exist_ok=True)
        self.BACKUP_DIR.mkdir(exist_ok=True)

    def _load(self):
        """Load settings from config file"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # Merge with defaults to handle new settings
                    defaults = self.default_settings()
                    defaults.update(saved)
                    return defaults
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_settings()
        return self.default_settings()

    def default_settings(self):
        """Return default configuration"""
        return {
            # Appearance
            "theme": "dark",
            "accent_color": "#9D46FF",
            
            # Editor
            "font_size": 13,
            "font_family": "JetBrains Mono",
            "word_wrap": True,
            "show_line_numbers": True,
            "tab_size": 4,
            "auto_save": False,
            "auto_save_interval": 60,  # seconds
            
            # Data
            "recent_files": [],
            "max_recent_files": 10,
            "session_tabs": [], # List of {name, path, is_backup}
            
            # Cloud
            "google_logged_in": False,
            
            # Window
            "window_width": 1280,
            "window_height": 720,
            "window_maximized": False,
        }

    def save(self):
        """Save current settings to config file"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_recent_file(self, path):
        """Add a file to recent files list"""
        path_str = str(path)
        
        # Remove if already exists (to move to front)
        if path_str in self.settings["recent_files"]:
            self.settings["recent_files"].remove(path_str)
            
        # Insert at front
        self.settings["recent_files"].insert(0, path_str)
        
        # Limit to max recent files
        max_files = self.settings.get("max_recent_files", 10)
        self.settings["recent_files"] = self.settings["recent_files"][:max_files]
        
        self.save()
        
    def remove_recent_file(self, path):
        """Remove a file from recent files list"""
        path_str = str(path)
        if path_str in self.settings["recent_files"]:
            self.settings["recent_files"].remove(path_str)
            self.save()
            
    def clear_recent_files(self):
        """Clear all recent files"""
        self.settings["recent_files"] = []
        self.save()
        
    def get(self, key, default=None):
        """Get a setting value with optional default"""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save()


# Global config instance
config = Config()

"""
Drive Service Stub
Placeholder for future Google Drive integration.
"""
from src.logic.config import config

class DriveService:
    def __init__(self):
        self.service = None
        
    def authenticate(self):
        """Stub authentication"""
        print("Google Drive integration is currently disabled.")
        return False

    def logout(self):
        """Stub logout"""
        config.settings["google_logged_in"] = False
        config.save()

    def list_notes(self):
        """Stub list"""
        return []

    def upload_note(self, name, content, file_id=None):
        """Stub upload"""
        return None

    def download_note(self, file_id):
        """Stub download"""
        return None

drive_service = DriveService()
BaseDriveException = Exception

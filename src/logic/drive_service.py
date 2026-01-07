"""
=============================================================================
FUTURE: Google Drive Integration
=============================================================================
Status: NOT YET IMPLEMENTED - UI is hidden
To enable: Set ENABLE_CLOUD = True in src/logic/config.py
=============================================================================

TODO: Implement actual Google Drive OAuth2 authentication and API calls.
Current stub defines the expected interface:
- authenticate(): Returns True on successful OAuth flow
- list_notes(): Returns list of {"id": str, "name": str, "modifiedTime": str}
- upload_note(name, content, file_id=None): Uploads/updates a note
- download_note(file_id): Returns note content as string
- logout(): Clears credentials and updates config
"""

from src.logic.config import config


class DriveService:
    """Stub - implement Google Drive API integration"""

    def __init__(self):
        self.service = None

    def authenticate(self) -> bool:
        raise NotImplementedError("TODO: Implement Google Drive OAuth2")

    def logout(self) -> None:
        raise NotImplementedError("TODO: Implement Google Drive logout")

    def list_notes(self) -> list[dict]:
        raise NotImplementedError("TODO: Implement Google Drive list_notes")

    def upload_note(self, name: str, content: str, file_id: str | None = None) -> None:
        raise NotImplementedError("TODO: Implement Google Drive upload_note")

    def download_note(self, file_id: str) -> str:
        raise NotImplementedError("TODO: Implement Google Drive download_note")


drive_service = DriveService()
BaseDriveException = Exception

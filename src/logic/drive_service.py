import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from src.logic.config import config

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.token_path = config.APP_DIR / 'token.json'
        
        # Check both the app config dir and the current working directory for credentials
        self.creds_path = config.APP_DIR / 'credentials.json'
        if not self.creds_path.exists() and os.path.exists("credentials.json"):
            self.creds_path = Path("credentials.json")

    def authenticate(self):
        """Performs browser-based OAuth2 authentication"""
        if os.path.exists(self.token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                print(f"Error loading saved token: {e}")
                self.creds = None
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None
            
            if not self.creds or not self.creds.valid:
                if not self.creds_path.exists():
                    raise FileNotFoundError(f"credentials.json not found. Please place it in {self.creds_path.parent} or the project root.")
                
                flow = InstalledAppFlow.from_client_secrets_file(str(self.creds_path), SCOPES)
                # This explicitly opens the browser
                self.creds = flow.run_local_server(port=0, prompt='consent')
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('drive', 'v3', credentials=self.creds)
        config.settings["google_logged_in"] = True
        config.save()
        return True

    def logout(self):
        """Removes local token and clears credentials"""
        if self.token_path.exists():
            try:
                self.token_path.unlink()
            except Exception as e:
                print(f"Error deleting token: {e}")
        
        self.creds = None
        self.service = None
        config.settings["google_logged_in"] = False
        config.save()

    def list_notes(self):
        if not self.service: return []
        try:
            results = self.service.files().list(
                pageSize=20, 
                fields="nextPageToken, files(id, name)",
                q="mimeType='text/plain' and trashed=false"
            ).execute()
            return results.get('files', [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def upload_note(self, name, content, file_id=None):
        if not self.service: return None
        
        file_metadata = {'name': name, 'mimeType': 'text/plain'}
        
        # Create a temporary file buffer
        bio = io.BytesIO(content.encode('utf-8'))
        media = MediaFileUpload(None, mimetype='text/plain', resumable=True)
        # Actually MediaFileUpload usually takes a path. For buffer use MediaIoBaseUpload
        from googleapiclient.http import MediaIoBaseUpload
        media = MediaIoBaseUpload(bio, mimetype='text/plain', resumable=True)

        if file_id:
            file = self.service.files().update(fileId=file_id, media_body=media).execute()
        else:
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        return file.get('id')

    def download_note(self, file_id):
        if not self.service: return None
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh.getvalue().decode('utf-8')

drive_service = DriveService()
BaseDriveException = HttpError

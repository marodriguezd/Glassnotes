import os
from pathlib import Path

from src.logic.config import Config


class FileManager:
    @staticmethod
    def save_file(path, content):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False

    @staticmethod
    def read_file(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading: {e}")
            return None

    @staticmethod
    def list_files(directory):
        """List all supported text files in directory"""
        files = []
        try:
            if not os.path.exists(directory):
                return []

            for file in os.listdir(directory):
                if file.lower().endswith(Config.SUPPORTED_TEXT_FORMATS):
                    files.append(str(Path(directory) / file))
        except Exception as e:
            print(f"Error listing files: {e}")
        return files

    @staticmethod
    def delete_file(path):
        """Delete a file"""
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
        return False


file_manager = FileManager()

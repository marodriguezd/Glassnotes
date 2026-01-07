import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, List

from src.logic.config import Config


@lru_cache(maxsize=128)
def _get_file_preview_cached(path: str, max_bytes: int = 200) -> str:
    """Cached file preview - use cache key (path, max_bytes)"""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_bytes)
    except Exception:
        return ""


def clear_preview_cache():
    """Clear the preview cache - call when files change"""
    _get_file_preview_cached.cache_clear()


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
    def get_file_preview(path: str, max_bytes: int = 200) -> str:
        """Get first few lines of a file as preview (cached)"""
        return _get_file_preview_cached(path, max_bytes)

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

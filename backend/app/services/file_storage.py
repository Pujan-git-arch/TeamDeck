from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class FileStorageService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file: UploadFile, stored_name: str) -> Path:
        file_path = self.upload_dir / stored_name

        with file_path.open("wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                buffer.write(chunk)

        return file_path

    def get_file_path(self, stored_name: str) -> Path:
        return self.upload_dir / stored_name

    def delete_file(self, stored_name: str) -> None:
        file_path = self.get_file_path(stored_name)

        if file_path.exists():
            file_path.unlink()
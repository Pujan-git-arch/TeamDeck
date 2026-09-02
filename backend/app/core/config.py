from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # Try relative path first, fallback to absolute path
    _env_file = Path(".env")
    if not _env_file.exists():
        _env_file = Path(__file__).parent.parent.parent / ".env"

    model_config = SettingsConfigDict(
        env_file=str(_env_file),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
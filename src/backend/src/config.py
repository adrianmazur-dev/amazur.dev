import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str
    linkedin_access_token: str | None = field(default=None, repr=False)
    linkedin_client_id: str | None = field(default=None, repr=False)
    linkedin_client_secret: str | None = field(default=None, repr=False)
    linkedin_timeout_seconds: int | None = field(default=15)


def _get_secret(name: str) -> str | None:
    if file_path := os.getenv(f"{name}_FILE"):
        value = Path(file_path).read_text(encoding="utf-8").strip()
        return value or None

    if value := os.getenv(name):
        return value.strip() or None

    return None


def load_settings() -> Settings:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/database.db"),
        linkedin_access_token=_get_secret("LINKEDIN_ACCESS_TOKEN"),
        linkedin_client_id=_get_secret("LINKEDIN_CLIENT_ID"),
        linkedin_client_secret=_get_secret("LINKEDIN_CLIENT_SECRET"),
    )

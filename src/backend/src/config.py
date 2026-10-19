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


def load_settings() -> Settings:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/database.db"),
        linkedin_access_token=os.getenv("LINKEDIN_ACCESS_TOKEN"),
        linkedin_client_id=os.getenv("LINKEDIN_CLIENT_ID"),
        linkedin_client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
    )

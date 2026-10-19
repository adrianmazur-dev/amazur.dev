from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LinkedInSyncStatus:
    last_synced_at: datetime | None
    next_sync_at: datetime | None

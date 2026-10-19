from typing import Protocol

from modules.linkedin.domain.sync_status import LinkedInSyncStatus


class LinkedInSyncStatusReader(Protocol):
    async def get_sync_status(self) -> LinkedInSyncStatus: ...

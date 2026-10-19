from datetime import datetime
from typing import Protocol

from modules.linkedin.application.ports.reader import LinkedInReader
from modules.linkedin.domain.snapshot import LinkedInSnapshot


class LinkedInRepository(LinkedInReader, Protocol):
    async def get_synced_at(self) -> datetime | None: ...

    async def replace(self, snapshot: LinkedInSnapshot) -> None: ...

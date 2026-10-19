from typing import Protocol


class LinkedInProbe(Protocol):
    async def is_available(self) -> bool: ...

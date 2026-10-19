from typing import Protocol

from modules.health.domain.health import DependencyStatus


class LinkedInProbe(Protocol):
    async def check(self) -> DependencyStatus: ...

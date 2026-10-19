import asyncio

from modules.health.application.ports.database_probe import DatabaseProbe
from modules.health.application.ports.linkedin_probe import LinkedInProbe
from modules.health.domain.health import DependencyStatus, HealthStatus


class CheckHealth:
    def __init__(self, database_probe: DatabaseProbe, linkedin_probe: LinkedInProbe) -> None:
        self.database_probe = database_probe
        self.linkedin_probe = linkedin_probe

    async def execute(self) -> HealthStatus:
        database_available, linkedin_available = await asyncio.gather(
            asyncio.to_thread(self.database_probe.is_available),
            self.linkedin_probe.is_available(),
        )
        return HealthStatus(
            checks=(
                DependencyStatus(
                    "database",
                    database_available,
                ),
                DependencyStatus(
                    "linkedin",
                    linkedin_available,
                ),
            )
        )

import asyncio

from modules.health.application.ports.database_probe import DatabaseProbe
from modules.health.application.ports.linkedin_probe import LinkedInProbe
from modules.health.domain.health import HealthStatus


class CheckHealth:
    def __init__(self, database_probe: DatabaseProbe, linkedin_probe: LinkedInProbe) -> None:
        self.database_probe = database_probe
        self.linkedin_probe = linkedin_probe

    async def execute(self) -> HealthStatus:
        database_status, linkedin_status = await asyncio.gather(
            asyncio.to_thread(self.database_probe.check),
            self.linkedin_probe.check(),
        )
        return HealthStatus(checks=(database_status, linkedin_status))

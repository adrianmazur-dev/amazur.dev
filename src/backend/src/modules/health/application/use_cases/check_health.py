from modules.health.application.ports.database_probe import DatabaseProbe
from modules.health.domain.health import DependencyStatus, HealthStatus


class CheckHealth:
    def __init__(self, database_probe: DatabaseProbe):
        self.database_probe = database_probe

    def execute(self) -> HealthStatus:
        return HealthStatus(
            checks=(
                DependencyStatus(
                    "database",
                    self.database_probe.is_available(),
                ),
            )
        )

from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    available: bool


@dataclass(frozen=True)
class HealthStatus:
    checks: tuple[DependencyStatus, ...]

    @property
    def ready(self) -> bool:
        return all(check.available for check in self.checks)

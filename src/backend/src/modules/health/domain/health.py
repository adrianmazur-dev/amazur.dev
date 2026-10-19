from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    available: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HealthStatus:
    checks: tuple[DependencyStatus, ...]

    @property
    def ready(self) -> bool:
        return all(check.available for check in self.checks)

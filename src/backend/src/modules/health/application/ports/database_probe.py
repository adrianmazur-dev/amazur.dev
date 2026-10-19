from typing import Protocol

from modules.health.domain.health import DependencyStatus


class DatabaseProbe(Protocol):
    def check(self) -> DependencyStatus: ...

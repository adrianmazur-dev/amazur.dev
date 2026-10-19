from typing import Protocol


class DatabaseProbe(Protocol):
    def is_available(self) -> bool: ...

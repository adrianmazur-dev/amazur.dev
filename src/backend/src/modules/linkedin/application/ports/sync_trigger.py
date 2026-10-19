from typing import Protocol, runtime_checkable


@runtime_checkable
class LinkedInSyncTrigger(Protocol):
    def request_sync(self) -> None: ...

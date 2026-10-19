import asyncio
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from math import ceil
from time import monotonic

import structlog

from modules.linkedin.application.errors import LinkedInError
from modules.linkedin.application.ports.repository import LinkedInRepository
from modules.linkedin.application.ports.sync_trigger import LinkedInSyncTrigger
from modules.linkedin.application.use_cases.sync_linkedin_data import SyncLinkedInData

logger = structlog.get_logger(__name__)

SYNC_INTERVAL = timedelta(hours=6)
RETRY_DELAY_SECONDS = 300


def _retry_delay_seconds(retry_after: str | None) -> float:
    if not retry_after:
        return RETRY_DELAY_SECONDS

    now = datetime.now(UTC)
    try:
        value = retry_after.strip()
        if value.isascii() and value.isdigit():
            retry_at = now + timedelta(seconds=int(value))
        else:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                return RETRY_DELAY_SECONDS
        return max(RETRY_DELAY_SECONDS, (retry_at - now).total_seconds())
    except ValueError, TypeError, OverflowError:
        return RETRY_DELAY_SECONDS


def _scheduled_delay_seconds(synced_at: datetime | None, *, now: datetime) -> float:
    if synced_at is None:
        return 0.0
    return max(0.0, (synced_at + SYNC_INTERVAL - now).total_seconds())


class LinkedInSyncJob(LinkedInSyncTrigger):
    def __init__(self, sync: SyncLinkedInData, repository: LinkedInRepository) -> None:
        self._sync = sync
        self._repository = repository
        self._requested = asyncio.Event()
        self._synchronizing = False
        self._retry_not_before: float | None = None

    def request_sync(self) -> None:
        if self._synchronizing or self._requested.is_set():
            logger.info("LinkedIn synchronization request merged with existing work")
            return
        self._requested.set()
        logger.info("LinkedIn synchronization requested")

    async def run(self) -> None:
        logger.info("LinkedIn synchronization job started", interval_seconds=SYNC_INTERVAL.total_seconds())
        try:
            while True:
                if self._retry_not_before is not None:
                    remaining = self._retry_not_before - monotonic()
                    if remaining > 0:
                        await asyncio.sleep(remaining)
                delay = await self._run_once()
                logger.info(
                    "Next LinkedIn synchronization check scheduled",
                    next_run_at=(datetime.now(UTC) + timedelta(seconds=delay)).isoformat(),
                    delay_seconds=round(delay),
                )
                with suppress(TimeoutError):
                    await asyncio.wait_for(self._requested.wait(), timeout=delay)
        finally:
            self._synchronizing = False
            self._requested.clear()
            logger.info("LinkedIn synchronization job stopped")

    async def _run_once(self) -> float:
        try:
            synced_at = await self._repository.get_synced_at()
            delay = _scheduled_delay_seconds(synced_at, now=datetime.now(UTC))
            trigger = self._get_trigger(delay)
            if trigger is None:
                logger.info("LinkedIn synchronization skipped; stored data is up to date")
                return max(1.0, delay)

            synced_at = await self._synchronize(trigger)
            self._retry_not_before = None
            return max(1.0, _scheduled_delay_seconds(synced_at, now=datetime.now(UTC)))
        except LinkedInError as exc:
            delay = _retry_delay_seconds(exc.retry_after)
            logger.warning("LinkedIn synchronization failed", code=exc.code.value, retry_in_seconds=ceil(delay))
        except Exception as exc:
            delay = RETRY_DELAY_SECONDS
            logger.error(
                "LinkedIn synchronization job failed",
                error_type=type(exc).__name__,
                retry_in_seconds=RETRY_DELAY_SECONDS,
            )

        self._requested.clear()
        self._retry_not_before = monotonic() + delay
        return delay

    def _get_trigger(self, scheduled_delay: float) -> str | None:
        if self._requested.is_set():
            return "manual"
        if self._retry_not_before is not None:
            return "retry"
        return "scheduled" if scheduled_delay <= 0 else None

    async def _synchronize(self, trigger: str) -> datetime:
        self._requested.clear()
        self._synchronizing = True
        try:
            logger.info("LinkedIn synchronization started", trigger=trigger)
            snapshot = await self._sync.execute()
        finally:
            self._synchronizing = False
        logger.info(
            "LinkedIn data synchronized",
            synced_at=snapshot.synced_at.isoformat(),
            experience_count=len(snapshot.experience),
            education_count=len(snapshot.education),
            certifications_count=len(snapshot.certifications),
        )
        return snapshot.synced_at

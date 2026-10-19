import asyncio
from datetime import UTC, datetime

import httpx
import structlog

from modules.health.application.ports.linkedin_probe import LinkedInProbe
from modules.health.domain.health import DependencyStatus
from modules.linkedin.application.ports.sync_status_reader import LinkedInSyncStatusReader
from modules.linkedin.domain.sync_status import LinkedInSyncStatus

logger = structlog.get_logger(__name__)

INTROSPECTION_URL = "https://www.linkedin.com/oauth/v2/introspectToken"


class LinkedInApiProbe(LinkedInProbe):
    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        client_id: str | None,
        client_secret: str | None,
        access_token: str | None,
        sync_status_reader: LinkedInSyncStatusReader,
    ) -> None:
        self._client = client
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token
        self._sync_status_reader = sync_status_reader

    async def check(self) -> DependencyStatus:
        token_status, sync_status = await asyncio.gather(self._check_token(), self._get_sync_status())
        return DependencyStatus(
            "linkedin",
            token_status.available,
            {
                **token_status.details,
                "last_synced_at": (
                    sync_status.last_synced_at.isoformat() if sync_status and sync_status.last_synced_at else None
                ),
                "next_sync_at": sync_status.next_sync_at.isoformat()
                if sync_status and sync_status.next_sync_at
                else None,
            },
        )

    async def _get_sync_status(self) -> LinkedInSyncStatus | None:
        try:
            return await self._sync_status_reader.get_sync_status()
        except Exception as exc:
            logger.warning("LinkedIn synchronization status check failed", error_type=type(exc).__name__)
            return None

    async def _check_token(self) -> DependencyStatus:
        if not self._client_id or not self._client_secret or not self._access_token:
            logger.warning("LinkedIn health check failed", code="not_configured")
            return DependencyStatus("linkedin", False, {"status": "not_configured", "expires_at": None})

        try:
            response = await self._client.post(
                INTROSPECTION_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "token": self._access_token,
                },
                follow_redirects=False,
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as exc:
            logger.warning("LinkedIn health check failed", code=type(exc).__name__)
            return DependencyStatus("linkedin", False, {"status": "unavailable", "expires_at": None})
        except ValueError:
            logger.warning("LinkedIn health check failed", code="invalid_response")
            return DependencyStatus("linkedin", False, {"status": "invalid_response", "expires_at": None})

        if not isinstance(payload, dict) or not isinstance(payload.get("active"), bool):
            logger.warning("LinkedIn health check failed", code="invalid_response")
            return DependencyStatus("linkedin", False, {"status": "invalid_response", "expires_at": None})

        active = payload["active"]
        if not active:
            logger.warning("LinkedIn health check failed", code="inactive_token")
        status = payload.get("status")
        if not isinstance(status, str) or status not in {"active", "expired", "revoked"}:
            status = "active" if active else "inactive"
        expires_at = payload.get("expires_at")
        expiry = None
        if isinstance(expires_at, int) and not isinstance(expires_at, bool):
            try:
                expiry = datetime.fromtimestamp(expires_at, UTC).isoformat()
            except ValueError, OverflowError, OSError:
                logger.warning("LinkedIn token expiry is invalid")
        return DependencyStatus("linkedin", active, {"status": status, "expires_at": expiry})

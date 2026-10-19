import httpx
import structlog

from modules.health.application.ports.linkedin_probe import LinkedInProbe

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
    ) -> None:
        self._client = client
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token

    async def is_available(self) -> bool:
        if not self._client_id or not self._client_secret or not self._access_token:
            logger.warning("LinkedIn health check failed", code="not_configured")
            return False

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
            return False
        except ValueError:
            logger.warning("LinkedIn health check failed", code="invalid_response")
            return False

        active = isinstance(payload, dict) and payload.get("active") is True
        if not active:
            logger.warning("LinkedIn health check failed", code="inactive_token")
        return active

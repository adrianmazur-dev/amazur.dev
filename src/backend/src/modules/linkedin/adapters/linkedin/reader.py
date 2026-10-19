from enum import StrEnum

import httpx

from modules.linkedin.adapters.linkedin.snapshot_mapper import (
    SnapshotRow,
    map_certification,
    map_education,
    map_experience,
    map_profile,
)
from modules.linkedin.application.errors import LinkedInError, LinkedInErrorCode
from modules.linkedin.application.ports.reader import LinkedInReader
from modules.linkedin.domain.profile import Certification, Education, Experience, LinkedInProfile

SNAPSHOT_URL = "https://api.linkedin.com/rest/memberSnapshotData"
API_VERSION = "202312"
MAX_SNAPSHOT_PAGES = 100
NO_DATA_MESSAGES = {
    "No data found for this memberId",
    "No data found for this memberId.",
    "No data found for this domain and memberId",
    "No data found for this domain and memberId.",
}


class SnapshotDomain(StrEnum):
    PROFILE = "PROFILE"
    POSITIONS = "POSITIONS"
    EDUCATION = "EDUCATION"
    CERTIFICATIONS = "CERTIFICATIONS"


class LinkedInApiReader(LinkedInReader):
    def __init__(self, client: httpx.AsyncClient, access_token: str | None) -> None:
        self._client = client
        self._access_token = access_token.strip() if access_token else None

    async def get_profile(self) -> LinkedInProfile | None:
        rows = await self._read_snapshot(SnapshotDomain.PROFILE)
        if len(rows) > 1:
            raise LinkedInError(LinkedInErrorCode.INVALID_RESPONSE, "LinkedIn returned more than one profile.")
        return map_profile(rows[0]) if rows else None

    async def get_experience(self) -> list[Experience]:
        return [map_experience(row) for row in await self._read_snapshot(SnapshotDomain.POSITIONS)]

    async def get_education(self) -> list[Education]:
        return [map_education(row) for row in await self._read_snapshot(SnapshotDomain.EDUCATION)]

    async def get_certifications(self) -> list[Certification]:
        return [map_certification(row) for row in await self._read_snapshot(SnapshotDomain.CERTIFICATIONS)]

    async def _read_snapshot(self, domain: SnapshotDomain) -> list[SnapshotRow]:
        if not self._access_token:
            raise LinkedInError(
                LinkedInErrorCode.NOT_CONFIGURED,
                "Set LINKEDIN_ACCESS_TOKEN in the backend environment or .env file.",
                domain=domain,
            )

        rows: list[SnapshotRow] = []
        previous_page: list[SnapshotRow] | None = None
        for page in range(MAX_SNAPSHOT_PAGES):
            page_rows = await self._read_page(domain, page)
            if not page_rows:
                return rows
            if page_rows == previous_page:
                raise LinkedInError(
                    LinkedInErrorCode.INVALID_RESPONSE,
                    "LinkedIn returned a repeated snapshot page; the download could not be completed.",
                    domain=domain,
                )
            rows.extend(page_rows)
            previous_page = page_rows

        raise LinkedInError(
            LinkedInErrorCode.INVALID_RESPONSE,
            "LinkedIn snapshot exceeded the pagination limit; the download could not be completed.",
            domain=domain,
        )

    async def _read_page(self, domain: SnapshotDomain, page: int) -> list[SnapshotRow] | None:
        try:
            response = await self._client.get(
                SNAPSHOT_URL,
                params={"q": "criteria", "domain": domain.value, "start": page},
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Linkedin-Version": API_VERSION,
                    "Accept": "application/json",
                },
                follow_redirects=False,
            )
        except httpx.TimeoutException:
            raise LinkedInError(LinkedInErrorCode.TIMEOUT, "LinkedIn did not respond in time.", domain=domain) from None
        except httpx.RequestError:
            raise LinkedInError(
                LinkedInErrorCode.UNAVAILABLE, "Could not connect to LinkedIn.", domain=domain
            ) from None

        if response.status_code in {401, 403}:
            raise LinkedInError(
                LinkedInErrorCode.ACCESS_DENIED,
                "LinkedIn rejected the access token. Check its expiry and the r_dma_portability_self_serve permission.",
                domain=domain,
            )
        if response.status_code == 429:
            raise LinkedInError(
                LinkedInErrorCode.RATE_LIMITED,
                "LinkedIn API request limit reached. Try again later.",
                domain=domain,
                retry_after=response.headers.get("Retry-After"),
            )
        if response.status_code >= 500:
            raise LinkedInError(
                LinkedInErrorCode.UNAVAILABLE,
                "LinkedIn API is temporarily unavailable.",
                domain=domain,
                retry_after=response.headers.get("Retry-After"),
            )

        try:
            payload = response.json()
        except ValueError:
            raise LinkedInError(
                LinkedInErrorCode.INVALID_RESPONSE, "LinkedIn returned an invalid JSON response.", domain=domain
            ) from None

        if not isinstance(payload, dict):
            raise LinkedInError(
                LinkedInErrorCode.INVALID_RESPONSE, "LinkedIn returned an unexpected response format.", domain=domain
            )
        message = payload.get("message")
        if response.status_code == 404 and isinstance(message, str) and message in NO_DATA_MESSAGES:
            return None
        if not response.is_success:
            raise LinkedInError(
                LinkedInErrorCode.INVALID_RESPONSE,
                f"LinkedIn API returned HTTP {response.status_code}.",
                domain=domain,
            )

        elements = payload.get("elements")
        if not isinstance(elements, list):
            raise LinkedInError(
                LinkedInErrorCode.INVALID_RESPONSE, "LinkedIn response is missing snapshot elements.", domain=domain
            )
        rows: list[SnapshotRow] = []
        for element in elements:
            if not isinstance(element, dict) or element.get("snapshotDomain") != domain:
                raise LinkedInError(
                    LinkedInErrorCode.INVALID_RESPONSE,
                    "LinkedIn returned an unexpected snapshot domain.",
                    domain=domain,
                )
            snapshot_data = element.get("snapshotData")
            if not isinstance(snapshot_data, list) or any(not isinstance(row, dict) for row in snapshot_data):
                raise LinkedInError(
                    LinkedInErrorCode.INVALID_RESPONSE, "LinkedIn returned invalid snapshot records.", domain=domain
                )
            rows.extend(snapshot_data)
        return rows

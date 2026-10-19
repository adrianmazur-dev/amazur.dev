from enum import StrEnum


class LinkedInErrorCode(StrEnum):
    NOT_CONFIGURED = "linkedin_not_configured"
    ACCESS_DENIED = "linkedin_access_denied"
    RATE_LIMITED = "linkedin_rate_limited"
    TIMEOUT = "linkedin_timeout"
    UNAVAILABLE = "linkedin_unavailable"
    INVALID_RESPONSE = "linkedin_invalid_response"
    DATA_UNAVAILABLE = "linkedin_data_unavailable"
    STORAGE_UNAVAILABLE = "linkedin_storage_unavailable"


class LinkedInError(Exception):
    def __init__(
        self,
        code: LinkedInErrorCode,
        detail: str,
        *,
        domain: str | None = None,
        retry_after: str | None = None,
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.domain = domain
        self.retry_after = retry_after

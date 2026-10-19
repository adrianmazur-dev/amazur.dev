import structlog
from litestar import Request, Response, Router, get, post
from litestar.di import NamedDependency, Provide

from modules.linkedin.adapters.http.dto import (
    CertificationDTO,
    EducationDTO,
    ExperienceDTO,
    LinkedInProfileDTO,
)
from modules.linkedin.application.errors import LinkedInError, LinkedInErrorCode
from modules.linkedin.application.ports.sync_trigger import LinkedInSyncTrigger
from modules.linkedin.application.use_cases.get_linkedin_data import GetLinkedInData
from modules.linkedin.domain.profile import Certification, Education, Experience, LinkedInProfile

logger = structlog.get_logger(__name__)

ERROR_STATUS_CODES = {
    LinkedInErrorCode.NOT_CONFIGURED: 503,
    LinkedInErrorCode.ACCESS_DENIED: 503,
    LinkedInErrorCode.RATE_LIMITED: 503,
    LinkedInErrorCode.TIMEOUT: 504,
    LinkedInErrorCode.UNAVAILABLE: 503,
    LinkedInErrorCode.INVALID_RESPONSE: 502,
    LinkedInErrorCode.DATA_UNAVAILABLE: 503,
    LinkedInErrorCode.STORAGE_UNAVAILABLE: 503,
}


def linkedin_error_handler(request: Request, exc: LinkedInError) -> Response[dict[str, str]]:
    status_code = ERROR_STATUS_CODES[exc.code]
    logger.warning("LinkedIn request failed", path=request.url.path, domain=exc.domain, code=exc.code.value)
    headers = {"Cache-Control": "no-store"}
    if exc.retry_after:
        headers["Retry-After"] = exc.retry_after
    return Response(
        content={"code": exc.code.value, "detail": exc.detail},
        status_code=status_code,
        headers=headers,
    )


@get(path="/profile", return_dto=LinkedInProfileDTO, summary="Get LinkedIn profile")
async def profile(linkedin_data: NamedDependency[GetLinkedInData]) -> LinkedInProfile:
    return await linkedin_data.get_profile()


@get(path="/experience", return_dto=ExperienceDTO, summary="Get LinkedIn work experience")
async def experience(linkedin_data: NamedDependency[GetLinkedInData]) -> list[Experience]:
    return await linkedin_data.get_experience()


@get(path="/education", return_dto=EducationDTO, summary="Get LinkedIn education")
async def education(linkedin_data: NamedDependency[GetLinkedInData]) -> list[Education]:
    return await linkedin_data.get_education()


@get(path="/certifications", return_dto=CertificationDTO, summary="Get LinkedIn certifications")
async def certifications(linkedin_data: NamedDependency[GetLinkedInData]) -> list[Certification]:
    return await linkedin_data.get_certifications()


@post(path="/sync", status_code=202, summary="Request LinkedIn synchronization")
async def synchronize(sync_trigger: NamedDependency[LinkedInSyncTrigger]) -> None:
    sync_trigger.request_sync()


def create_router(linkedin_data: GetLinkedInData, sync_trigger: LinkedInSyncTrigger) -> Router:
    def provide_linkedin_data() -> GetLinkedInData:
        return linkedin_data

    def provide_sync_trigger() -> LinkedInSyncTrigger:
        return sync_trigger

    return Router(
        path="/linkedin",
        tags=["linkedin"],
        route_handlers=[profile, experience, education, certifications, synchronize],
        dependencies={
            "linkedin_data": Provide(provide_linkedin_data, sync_to_thread=False),
            "sync_trigger": Provide(provide_sync_trigger, sync_to_thread=False),
        },
        exception_handlers={LinkedInError: linkedin_error_handler},
        response_headers={"Cache-Control": "no-store"},
    )

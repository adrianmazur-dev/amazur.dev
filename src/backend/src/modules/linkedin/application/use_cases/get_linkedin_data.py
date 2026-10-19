from modules.linkedin.application.errors import LinkedInError, LinkedInErrorCode
from modules.linkedin.application.ports.reader import LinkedInReader
from modules.linkedin.domain.profile import Certification, Education, Experience, LinkedInProfile


class GetLinkedInData:
    def __init__(self, reader: LinkedInReader) -> None:
        self.reader = reader

    async def get_profile(self) -> LinkedInProfile:
        profile = await self.reader.get_profile()
        if profile is None:
            raise LinkedInError(
                LinkedInErrorCode.DATA_UNAVAILABLE,
                "LinkedIn profile has not been synchronized yet.",
            )
        return profile

    async def get_experience(self) -> list[Experience]:
        return await self.reader.get_experience()

    async def get_education(self) -> list[Education]:
        return await self.reader.get_education()

    async def get_certifications(self) -> list[Certification]:
        return await self.reader.get_certifications()

from datetime import UTC, datetime

from modules.linkedin.application.errors import LinkedInError, LinkedInErrorCode
from modules.linkedin.application.ports.reader import LinkedInReader
from modules.linkedin.application.ports.repository import LinkedInRepository
from modules.linkedin.domain.snapshot import LinkedInSnapshot


class SyncLinkedInData:
    def __init__(self, reader: LinkedInReader, repository: LinkedInRepository) -> None:
        self.reader = reader
        self.repository = repository

    async def execute(self) -> LinkedInSnapshot:
        profile = await self.reader.get_profile()
        if profile is None:
            raise LinkedInError(
                LinkedInErrorCode.DATA_UNAVAILABLE, "LinkedIn profile is not available for synchronization."
            )

        experience = await self.reader.get_experience()
        education = await self.reader.get_education()
        certifications = await self.reader.get_certifications()
        snapshot = LinkedInSnapshot(
            profile=profile,
            experience=experience,
            education=education,
            certifications=certifications,
            synced_at=datetime.now(UTC),
        )
        await self.repository.replace(snapshot)
        return snapshot

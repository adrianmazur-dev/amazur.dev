from dataclasses import dataclass
from datetime import datetime

from modules.linkedin.domain.profile import Certification, Education, Experience, LinkedInProfile


@dataclass(frozen=True)
class LinkedInSnapshot:
    profile: LinkedInProfile
    experience: list[Experience]
    education: list[Education]
    certifications: list[Certification]
    synced_at: datetime

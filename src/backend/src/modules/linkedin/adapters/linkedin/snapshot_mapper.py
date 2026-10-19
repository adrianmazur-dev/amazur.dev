from typing import Any

from modules.linkedin.application.errors import LinkedInError, LinkedInErrorCode
from modules.linkedin.domain.profile import Certification, Education, Experience, LinkedInProfile

type SnapshotRow = dict[str, Any]


def _text(row: SnapshotRow, key: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise LinkedInError(LinkedInErrorCode.INVALID_RESPONSE, "LinkedIn returned an unexpected field type.")
    return value.strip() or None


def map_profile(row: SnapshotRow) -> LinkedInProfile:
    return LinkedInProfile(
        first_name=_text(row, "First Name"),
        last_name=_text(row, "Last Name"),
        headline=_text(row, "Headline"),
        summary=_text(row, "Summary"),
        industry=_text(row, "Industry"),
        location=_text(row, "Geo Location"),
    )


def map_experience(row: SnapshotRow) -> Experience:
    return Experience(
        company_name=_text(row, "Company Name"),
        title=_text(row, "Title"),
        description=_text(row, "Description"),
        location=_text(row, "Location"),
        start_date=_text(row, "Started On"),
        end_date=_text(row, "Finished On"),
    )


def map_education(row: SnapshotRow) -> Education:
    return Education(
        school_name=_text(row, "School Name"),
        degree=_text(row, "Degree Name"),
        notes=_text(row, "Notes"),
        activities=_text(row, "Activities"),
        start_date=_text(row, "Start Date"),
        end_date=_text(row, "End Date"),
    )


def map_certification(row: SnapshotRow) -> Certification:
    return Certification(
        name=_text(row, "Name"),
        authority=_text(row, "Authority"),
        license_number=_text(row, "License Number"),
        url=_text(row, "Url"),
        start_date=_text(row, "Started On"),
        end_date=_text(row, "Finished On"),
    )

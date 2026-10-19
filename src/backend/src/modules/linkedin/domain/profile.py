from dataclasses import dataclass


@dataclass(frozen=True)
class LinkedInProfile:
    first_name: str | None
    last_name: str | None
    headline: str | None
    summary: str | None
    industry: str | None
    location: str | None


@dataclass(frozen=True)
class Experience:
    company_name: str | None
    title: str | None
    description: str | None
    location: str | None
    start_date: str | None
    end_date: str | None


@dataclass(frozen=True)
class Education:
    school_name: str | None
    degree: str | None
    notes: str | None
    activities: str | None
    start_date: str | None
    end_date: str | None


@dataclass(frozen=True)
class Certification:
    name: str | None
    authority: str | None
    license_number: str | None
    url: str | None
    start_date: str | None
    end_date: str | None

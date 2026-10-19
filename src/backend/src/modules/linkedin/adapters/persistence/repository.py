import asyncio
from dataclasses import asdict
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from infrastructure.database import Base
from modules.linkedin.adapters.persistence.models import (
    CertificationRecord,
    EducationRecord,
    ExperienceRecord,
    LinkedInProfileRecord,
)
from modules.linkedin.application.errors import LinkedInError, LinkedInErrorCode
from modules.linkedin.application.ports.repository import LinkedInRepository
from modules.linkedin.domain.profile import Certification, Education, Experience, LinkedInProfile
from modules.linkedin.domain.snapshot import LinkedInSnapshot


class SqlAlchemyLinkedInRepository(LinkedInRepository):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def initialize(self) -> None:
        await asyncio.to_thread(Base.metadata.create_all, self._engine)

    async def get_synced_at(self) -> datetime | None:
        return await asyncio.to_thread(self._get_synced_at)

    def _get_synced_at(self) -> datetime | None:
        with Session(self._engine) as session:
            synced_at = session.scalar(select(LinkedInProfileRecord.synced_at).where(LinkedInProfileRecord.id == 1))
            if synced_at is None:
                return None
            return synced_at.replace(tzinfo=UTC) if synced_at.tzinfo is None else synced_at.astimezone(UTC)

    async def get_profile(self) -> LinkedInProfile | None:
        return await asyncio.to_thread(self._get_profile)

    def _get_profile(self) -> LinkedInProfile | None:
        with Session(self._engine) as session:
            record = session.get(LinkedInProfileRecord, 1)
            if record is None:
                return None
            return LinkedInProfile(
                first_name=record.first_name,
                last_name=record.last_name,
                headline=record.headline,
                summary=record.summary,
                industry=record.industry,
                location=record.location,
            )

    async def get_experience(self) -> list[Experience]:
        return await asyncio.to_thread(self._get_experience)

    def _get_experience(self) -> list[Experience]:
        with Session(self._engine) as session:
            records = session.scalars(select(ExperienceRecord).order_by(ExperienceRecord.id))
            return [
                Experience(
                    company_name=record.company_name,
                    title=record.title,
                    description=record.description,
                    location=record.location,
                    start_date=record.start_date,
                    end_date=record.end_date,
                )
                for record in records
            ]

    async def get_education(self) -> list[Education]:
        return await asyncio.to_thread(self._get_education)

    def _get_education(self) -> list[Education]:
        with Session(self._engine) as session:
            records = session.scalars(select(EducationRecord).order_by(EducationRecord.id))
            return [
                Education(
                    school_name=record.school_name,
                    degree=record.degree,
                    notes=record.notes,
                    activities=record.activities,
                    start_date=record.start_date,
                    end_date=record.end_date,
                )
                for record in records
            ]

    async def get_certifications(self) -> list[Certification]:
        return await asyncio.to_thread(self._get_certifications)

    def _get_certifications(self) -> list[Certification]:
        with Session(self._engine) as session:
            records = session.scalars(select(CertificationRecord).order_by(CertificationRecord.id))
            return [
                Certification(
                    name=record.name,
                    authority=record.authority,
                    license_number=record.license_number,
                    url=record.url,
                    start_date=record.start_date,
                    end_date=record.end_date,
                )
                for record in records
            ]

    async def replace(self, snapshot: LinkedInSnapshot) -> None:
        try:
            await asyncio.to_thread(self._replace, snapshot)
        except SQLAlchemyError:
            raise LinkedInError(
                LinkedInErrorCode.STORAGE_UNAVAILABLE, "Could not save LinkedIn data to the database."
            ) from None

    def _replace(self, snapshot: LinkedInSnapshot) -> None:
        with Session(self._engine) as session, session.begin():
            for model in (LinkedInProfileRecord, ExperienceRecord, EducationRecord, CertificationRecord):
                session.execute(delete(model))
            session.add(LinkedInProfileRecord(id=1, synced_at=snapshot.synced_at, **asdict(snapshot.profile)))
            session.add_all(
                ExperienceRecord(id=index, **asdict(item)) for index, item in enumerate(snapshot.experience, start=1)
            )
            session.add_all(
                EducationRecord(id=index, **asdict(item)) for index, item in enumerate(snapshot.education, start=1)
            )
            session.add_all(
                CertificationRecord(id=index, **asdict(item))
                for index, item in enumerate(snapshot.certifications, start=1)
            )

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

import httpx
import structlog
from litestar import Litestar

from config import load_settings
from infrastructure.database import build_engine
from infrastructure.logging import build_logging_plugin
from modules.health.adapters.http.router import (
    create_router as create_health_router,
)
from modules.health.adapters.linkedin.probe import LinkedInApiProbe
from modules.health.adapters.persistence.database_probe import (
    SqlAlchemyDatabaseProbe,
)
from modules.health.application.use_cases.check_health import CheckHealth
from modules.linkedin.adapters.http.router import create_router as create_linkedin_router
from modules.linkedin.adapters.linkedin.reader import LinkedInApiReader
from modules.linkedin.adapters.persistence.repository import SqlAlchemyLinkedInRepository
from modules.linkedin.adapters.scheduling.sync_job import LinkedInSyncJob
from modules.linkedin.application.use_cases.get_linkedin_data import GetLinkedInData
from modules.linkedin.application.use_cases.sync_linkedin_data import SyncLinkedInData

logger = structlog.get_logger(__name__)


def create_app() -> Litestar:
    settings = load_settings()
    engine = build_engine(settings.database_url)
    linkedin_client = httpx.AsyncClient(timeout=settings.linkedin_timeout_seconds)

    linkedin_reader = LinkedInApiReader(linkedin_client, settings.linkedin_access_token)
    linkedin_probe = LinkedInApiProbe(
        linkedin_client,
        client_id=settings.linkedin_client_id,
        client_secret=settings.linkedin_client_secret,
        access_token=settings.linkedin_access_token,
    )
    check_health = CheckHealth(SqlAlchemyDatabaseProbe(engine), linkedin_probe)
    linkedin_repository = SqlAlchemyLinkedInRepository(engine)
    linkedin_data = GetLinkedInData(linkedin_repository)
    sync_linkedin_data = SyncLinkedInData(linkedin_reader, linkedin_repository)
    linkedin_sync_job = LinkedInSyncJob(sync_linkedin_data, linkedin_repository)

    @asynccontextmanager
    async def lifespan(app: Litestar) -> AsyncGenerator[None]:
        sync_task: asyncio.Task[None] | None = None
        try:
            await linkedin_repository.initialize()
            sync_task = asyncio.create_task(linkedin_sync_job.run(), name="linkedin-sync")
            logger.info("Backend started")
            yield
        finally:
            try:
                if sync_task is not None:
                    sync_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await sync_task
            finally:
                try:
                    await linkedin_client.aclose()
                finally:
                    engine.dispose()
                    logger.info("Backend stopped")

    return Litestar(
        route_handlers=[
            create_health_router(check_health),
            create_linkedin_router(linkedin_data, linkedin_sync_job),
        ],
        lifespan=[lifespan],
        plugins=[build_logging_plugin()],
    )


app = create_app()


def dev() -> None:
    import sys
    from pathlib import Path

    from uvicorn import main as uvicorn_main

    source_dir = str(Path(__file__).resolve().parent)
    uvicorn_main(
        args=["main:app", "--reload", "--reload-dir", source_dir, *sys.argv[1:]],
        prog_name="dev",
    )


if __name__ == "__main__":
    dev()

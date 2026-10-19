from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from litestar import Litestar

from config import DATABASE_URL
from infrastructure.database import build_engine
from infrastructure.logging import build_logging_plugin
from modules.health.adapters.http.router import (
    create_router as create_health_router,
)
from modules.health.adapters.persistence.database_probe import (
    SqlAlchemyDatabaseProbe,
)
from modules.health.application.use_cases.check_health import CheckHealth

logger = structlog.get_logger(__name__)


def create_app() -> Litestar:
    engine = build_engine(DATABASE_URL)

    check_health = CheckHealth(SqlAlchemyDatabaseProbe(engine))

    @asynccontextmanager
    async def lifespan(app: Litestar) -> AsyncGenerator[None]:
        logger.info("Backend started")
        try:
            yield
        finally:
            engine.dispose()
            logger.info("Backend stopped")

    return Litestar(
        route_handlers=[
            create_health_router(check_health),
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

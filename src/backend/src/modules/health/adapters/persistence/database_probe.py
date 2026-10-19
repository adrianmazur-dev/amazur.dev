import structlog
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = structlog.get_logger(__name__)


class SqlAlchemyDatabaseProbe:
    def __init__(self, engine: Engine):
        self.engine = engine

    def is_available(self) -> bool:
        try:
            with self.engine.connect() as connection:
                return connection.execute(text("SELECT 1")).scalar_one() == 1
        except SQLAlchemyError:
            logger.warning("Database health check failed", exc_info=True)
            return False

import structlog
from sqlalchemy import func, inspect, select, table, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from modules.health.application.ports.database_probe import DatabaseProbe
from modules.health.domain.health import DependencyStatus

logger = structlog.get_logger(__name__)


class SqlAlchemyDatabaseProbe(DatabaseProbe):
    def __init__(self, engine: Engine):
        self.engine = engine

    def check(self) -> DependencyStatus:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1")).scalar_one()
                tables = {
                    name: int(connection.execute(select(func.count()).select_from(table(name))).scalar_one())
                    for name in sorted(inspect(connection).get_table_names())
                }
                return DependencyStatus("database", True, {"tables": tables})
        except SQLAlchemyError:
            logger.warning("Database health check failed", exc_info=True)
            return DependencyStatus("database", False, {"tables": None})

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str) -> Engine:
    url = make_url(database_url)
    connect_args = {}

    if url.get_backend_name() == "sqlite":
        connect_args["check_same_thread"] = False

        if url.database and url.database != ":memory:" and url.query.get("uri") != "true":
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)

    return create_engine(url=url, connect_args=connect_args, pool_pre_ping=True)

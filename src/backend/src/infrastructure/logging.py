import logging
import os

import structlog
from litestar.logging import StructLoggingConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin


def build_logging_plugin() -> StructlogPlugin:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = logging.getLevelNamesMapping().get(level_name)

    if level is None:
        raise ValueError(f"Invalid LOG_LEVEL: {level_name}")

    config = StructLoggingConfig(
        pretty_print_tty=False,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        log_exceptions="never",
    )

    if config.standard_lib_logging_config is not None:
        config.standard_lib_logging_config.root["level"] = level_name

    return StructlogPlugin(
        config=StructlogConfig(
            structlog_logging_config=config,
            enable_middleware_logging=False,
        )
    )

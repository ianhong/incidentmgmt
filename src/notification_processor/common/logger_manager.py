import logging
import os
import json
import structlog

class LoggerManager:
    _shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    def __init__(self):
        structlog.configure(
            processors=self._shared_processors
            + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer()
        )
        log_level = os.getenv("PUBSUB_LOG_LEVEL", "INFO").upper()
        log_format = os.getenv("PUBSUB_LOG_FORMAT", "console")

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer() if log_format == "json"
            else structlog.dev.ConsoleRenderer(colors=True),
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    def get_logger(self, name: str):
        return structlog.get_logger(name)

"""
Structured Logging Manager Module
"""

import logging
import os
import json
import structlog
import threading
import socket

class LoggerManager:
    """
    Centralized logger manager using structlog for structured logging.
    """
    _shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    def __init__(self):
        """
        Initialize the structured logging configuration.
        """
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
        """
        Get a structured logger instance for the given name.
        
        Args:
            name: The logger name (typically __name__ of the calling module)
            
        Returns:
            structlog.BoundLogger: Configured logger instance
        """
        return structlog.get_logger(name)

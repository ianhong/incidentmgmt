import logging
import os

class LoggerManager:
    """
    Centralized logger manager to standardize logging across the application.
    Allows different formats for info, warning, error, and critical levels.
    """
    DEFAULT_FORMATS = {
        logging.INFO: "%(asctime)s | INFO | %(name)s | %(message)s",
        logging.WARNING: "%(asctime)s | WARNING | %(name)s | %(message)s",
        logging.ERROR: "%(asctime)s | ERROR | %(name)s | %(message)s",
        logging.CRITICAL: "%(asctime)s | CRITICAL | %(name)s | %(message)s",
        logging.DEBUG: "%(asctime)s | DEBUG | %(name)s | %(message)s",
    }
    DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

    class LevelFormatter(logging.Formatter):
        def __init__(self, fmt_map, datefmt=None, default_fmt=None):
            super().__init__(fmt=default_fmt, datefmt=datefmt)
            self.fmt_map = fmt_map
            self.default_fmt = default_fmt or list(fmt_map.values())[0]

        def format(self, record):
            fmt = self.fmt_map.get(record.levelno, self.default_fmt)
            self._style._fmt = fmt
            return super().format(record)

    def __init__(self):
        self.logger = logging.getLogger()
        self.set_formats(self.DEFAULT_FORMATS, self.DEFAULT_DATEFMT)
        self.logger.setLevel(os.getenv("PUBSUB_LOG_LEVEL", "WARNING").upper())

    def set_formats(self, formats: dict, datefmt: str):
        handler_exists = any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers)
        if not handler_exists:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
        formatter = self.LevelFormatter(formats, datefmt, default_fmt=formats.get(logging.INFO))
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)

    def get_logger(self, name: str):
        self.logger.name = name
        return self.logger

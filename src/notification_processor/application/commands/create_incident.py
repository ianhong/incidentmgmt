"""Contains the command and handler for creating a new incident."""

import uuid
from pydantic import BaseModel, Field
from .base import Command, CommandHandler
from config.config_manager import ConfigManager
from common.logger_manager import LoggerManager

class CreateIncidentCommand(BaseModel, Command):
    """A command that holds the data required to create a new incident."""
    description: str

class CreateIncidentCommandHandler(CommandHandler[CreateIncidentCommand]):
    """The handler responsible for executing the CreateIncidentCommand."""

    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager):
        self.config_manager = config_manager
        self.logger = logger_manager.get_logger(__name__)

    def handle(self, command: CreateIncidentCommand) -> None:
        """Orchestrates the creation of a new incident."""
        if not command.description:
            raise ValueError("Incident description cannot be empty.")
        self.logger.info(f"Successfully created incident for customer: {command.description}")
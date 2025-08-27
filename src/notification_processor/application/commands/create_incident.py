"""
Create Incident Command and Handler Module
"""

import uuid
from pydantic import BaseModel, Field
from .base import Command, CommandHandler
from config.config_manager import ConfigManager
from common.logger_manager import LoggerManager

class CreateIncidentCommand(BaseModel, Command):
    """
    Command object that holds the data required to create a new incident.

    Attributes:
        description: Human-readable description of the incident
    """
    description: str

class CreateIncidentCommandHandler(CommandHandler[CreateIncidentCommand]):
    """
    Handler responsible for executing the CreateIncidentCommand.
    """

    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager):
        """
        Initialize the create incident command handler.

        Args:
            config_manager: Configuration manager for accessing settings
            logger_manager: Logger manager for structured logging
        """
        self.config_manager = config_manager
        self.logger = logger_manager.get_logger(__name__)

    def handle(self, command: CreateIncidentCommand) -> None:
        """
        Orchestrate the creation of a new incident.

        Args:
            command: The create incident command to process

        Raises:
            ValueError: If the incident description is empty or invalid
        """
        if not command.description:
            raise ValueError("Incident description cannot be empty.")
        self.logger.info(f"Successfully created incident for customer: {command.description}")

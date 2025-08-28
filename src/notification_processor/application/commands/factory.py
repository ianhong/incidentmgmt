"""
Command Factory Module
"""

from typing import Type
from application.commands.base import Command
from application.commands.create_incident import CreateIncidentCommand
from google.cloud import pubsub_v1

class CommandFactory:
    """
    Factory for creating command objects from raw data payloads.
    """

    def __init__(self):
        """
        Initialize the command factory with registered command types.
        """
        self._commands: dict[str, Type[Command]] = {
            "CreateIncident": CreateIncidentCommand,
            # Add other command names and their classes here
            # "ResolveIncident": ResolveIncidentCommand,
        }

    def create(self, message) -> Command:
        """
        Instantiate and return a command object based on the message content.

        Args:
            message: Pub/Sub message containing command data

        Returns:
            Command: An instance of a concrete command class

        Raises:
            ValueError: If the command type is not registered or message is invalid
        """

        payload = {
            "description": message.data.decode('utf-8')
        }

        command_class = self._commands.get("CreateIncident")
        if not command_class:
            raise ValueError(f"Unknown command type")

        # Pydantic models can be instantiated directly from a dictionary
        return command_class(**payload)

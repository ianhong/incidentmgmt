# infrastructure/commands/factory.py
from typing import Type
from application.commands.base import Command
from application.commands.create_incident import CreateIncidentCommand
from google.cloud import pubsub_v1

class CommandFactory:
    """
    Creates command objects from raw data payloads.
    """
    def __init__(self):
        self._commands: dict[str, Type[Command]] = {
            "CreateIncident": CreateIncidentCommand,
            # Add other command names and their classes here
            # "ResolveIncident": ResolveIncidentCommand,
        }

    def create(self, message) -> Command:
        """
        Instantiates and returns a command object based on the command name.

        Args:
            command_name: The string identifier for the command.
            payload: A dictionary containing the data for the command.

        Returns:
            An instance of a concrete command class.

        Raises:
            ValueError: If the command_name is not registered.
        """

        payload = {
            "description": message.data.decode('utf-8')
        }

        command_class = self._commands.get("CreateIncident")
        if not command_class:
            raise ValueError(f"Unknown command")

        # Pydantic models can be instantiated directly from a dictionary
        return command_class(**payload)
"""Contains the command and handler for creating a new incident."""

import uuid
from pydantic import BaseModel, Field
from .base import Command, CommandHandler

class CreateIncidentCommand(BaseModel, Command):
    """A command that holds the data required to create a new incident."""
    description: str

class CreateIncidentCommandHandler(CommandHandler[CreateIncidentCommand]):
    """The handler responsible for executing the CreateIncidentCommand."""

    def __init__(self):
        pass

    def handle(self, command: CreateIncidentCommand) -> None:
        """Orchestrates the creation of a new incident."""
        if not command.description:
            raise ValueError("Incident description cannot be empty.")
        print(f"Successfully created incident for customer: {command.description}")
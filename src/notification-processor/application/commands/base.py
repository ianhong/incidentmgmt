"""
Command Pattern Abstract Base Classes Module
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

class Command(ABC):
    """
    Abstract base class that serves as a marker for all command objects.
    """
    pass

# Define a generic type variable that must be a subclass of Command.
TCommand = TypeVar('TCommand', bound=Command)

class CommandHandler(Generic[TCommand], ABC):
    """
    Generic abstract base class for command handlers.

    Type Parameters:
        TCommand: The specific command type this handler processes
    """

    @abstractmethod
    def handle(self, command: TCommand) -> None:
        """
        Execute the business logic for a given command.

        Args:
            command: The command object containing the data for the action

        Raises:
            NotImplementedError: If not implemented by concrete handler
        """
        raise NotImplementedError

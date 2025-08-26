from abc import ABC, abstractmethod
from typing import Generic, TypeVar

class Command(ABC):
    """A base class that serves as a marker for all commands."""
    pass

# Define a generic type variable that must be a subclass of Command.
TCommand = TypeVar('TCommand', bound=Command)

class CommandHandler(Generic[TCommand], ABC):
    """A generic, abstract base class for a command handler."""
    
    @abstractmethod
    def handle(self, command: TCommand) -> None:
        """
        Executes the business logic for a given command.
        
        Args:
            command: The command object containing the data for the action.
        """
        raise NotImplementedError
# application/common/command.py
from abc import ABC, abstractmethod

class Command(ABC):
    """Abstract base class for all command objects."""
    
    @property
    @abstractmethod
    def command_name(self) -> str:
        """The unique name of the command."""
        raise NotImplementedError
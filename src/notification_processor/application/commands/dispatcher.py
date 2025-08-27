"""A dispatcher to route commands to their appropriate handlers."""

from typing import Type, Tuple
from dependency_injector.providers import Provider
from common.logger_manager import LoggerManager
from application.commands.base import Command, CommandHandler

class CommandDispatcher:
    """Uses a provider mapping to find and execute one or more command handlers."""

    def __init__(
        self,
        logger_manager: LoggerManager,
        handlers: dict[Type[Command], Tuple[Provider[CommandHandler], ...]],
    ):
        """
        Initializes the dispatcher.

        Args:
            handlers: A dictionary mapping command types to a tuple of their
                      corresponding handler providers from the DI container.
        """
        self._handlers = handlers
        self.logger = logger_manager.get_logger(__name__)

    def dispatch(self, command: Command) -> None:
        """Finds and executes all registered handlers for the given command."""
        
        # 1. Look up the tuple of handler providers for the command's type.
        handler_providers = self._handlers.get(type(command))
        
        if not handler_providers:
            raise ValueError(f"No handlers registered for command {type(command).__name__}")
        
        # 2. Iterate through each provider in the tuple.
        self.logger.info(f"Dispatching {type(command).__name__} to {len(handler_providers)} handler(s)...")
        for provider in handler_providers:
            # 3. Create an instance of the handler from the provider.
            handler = provider()
            
            # 4. Execute the handler's logic.
            handler.handle(command)
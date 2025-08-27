"""
Command Dispatcher Module
"""

from typing import Type, Tuple
from dependency_injector.providers import Provider
from common.logger_manager import LoggerManager
from application.commands.base import Command, CommandHandler

class CommandDispatcher:
    """
    Command dispatcher that routes commands to their appropriate handlers.
    """

    def __init__(
        self,
        logger_manager: LoggerManager,
        handlers: dict[Type[Command], Tuple[Provider[CommandHandler], ...]],
    ):
        """
        Initialize the command dispatcher.

        Args:
            logger_manager: Logger manager for structured logging
            handlers: Dictionary mapping command types to tuples of their
                     corresponding handler providers from the DI container
        """
        self._handlers = handlers
        self.logger = logger_manager.get_logger(__name__)

    def dispatch(self, command: Command) -> None:
        """
        Find and execute all registered handlers for the given command.

        Args:
            command: The command instance to dispatch

        Raises:
            ValueError: If no handlers are registered for the command type
        """

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

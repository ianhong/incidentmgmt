"""
Unit tests for the CommandDispatcher class.
"""

import pytest
from unittest.mock import Mock
from application.commands.dispatcher import CommandDispatcher
from application.commands.base import Command, CommandHandler
from common.logger_manager import LoggerManager
from dependency_injector.providers import Provider

class MockCommand(Command):
    """Mock command for unit testing."""
    def __init__(self, value: str):
        self.value = value

@pytest.fixture
def mock_logger_manager():
    """Create a mock logger manager."""
    logger_manager = Mock(spec=LoggerManager)
    mock_logger = Mock()  # Logger doesn't need spec as it's from structlog
    logger_manager.get_logger.return_value = mock_logger
    return logger_manager

@pytest.fixture
def mock_handler_provider():
    """Create a mock handler provider."""
    mock_handler = Mock(spec=CommandHandler)
    provider = Mock(spec=Provider)
    provider.return_value = mock_handler
    return provider, mock_handler

@pytest.fixture
def command_dispatcher(mock_logger_manager):
    """Create a CommandDispatcher instance for testing."""
    handlers = {}
    return CommandDispatcher(mock_logger_manager, handlers)

class TestCommandDispatcher:
    """Test suite for CommandDispatcher class."""

    def test_init_creates_logger(self, mock_logger_manager):
        """Test that __init__ properly creates a logger."""
        handlers = {}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        mock_logger_manager.get_logger.assert_called_once_with('application.commands.dispatcher')
        assert dispatcher._handlers == handlers

    def test_dispatch_single_handler_success(self, mock_logger_manager, mock_handler_provider):
        """Test successful dispatch to a single handler."""
        provider, mock_handler = mock_handler_provider
        command = MockCommand("test_value")

        handlers = {MockCommand: (provider,)}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        dispatcher.dispatch(command)

        provider.assert_called_once()
        mock_handler.handle.assert_called_once_with(command)

    def test_dispatch_multiple_handlers_success(self, mock_logger_manager):
        """Test successful dispatch to multiple handlers."""
        # Create multiple mock handlers
        provider1 = Mock(spec=Provider)
        handler1 = Mock(spec=CommandHandler)
        provider1.return_value = handler1

        provider2 = Mock(spec=Provider)
        handler2 = Mock(spec=CommandHandler)
        provider2.return_value = handler2

        command = MockCommand("test_value")
        handlers = {MockCommand: (provider1, provider2)}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        dispatcher.dispatch(command)

        # Verify both providers were called
        provider1.assert_called_once()
        provider2.assert_called_once()

        # Verify both handlers were called with the command
        handler1.handle.assert_called_once_with(command)
        handler2.handle.assert_called_once_with(command)

    def test_dispatch_no_handlers_raises_value_error(self, mock_logger_manager):
        """Test that dispatch raises ValueError when no handlers are registered."""
        command = MockCommand("test_value")
        handlers = {}  # Empty handlers dict
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        with pytest.raises(ValueError, match="No handlers registered for command MockCommand"):
            dispatcher.dispatch(command)

    def test_dispatch_logs_info_message(self, mock_logger_manager, mock_handler_provider):
        """Test that dispatch logs appropriate info messages."""
        provider, mock_handler = mock_handler_provider
        command = MockCommand("test_value")

        handlers = {MockCommand: (provider,)}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        mock_logger = mock_logger_manager.get_logger.return_value

        dispatcher.dispatch(command)

        mock_logger.info.assert_called_once_with(
            "Dispatching MockCommand to 1 handler(s)..."
        )

    def test_dispatch_logs_multiple_handlers_count(self, mock_logger_manager):
        """Test that dispatch logs correct handler count for multiple handlers."""
        # Create multiple mock handlers
        provider1 = Mock(spec=Provider)
        handler1 = Mock(spec=CommandHandler)
        provider1.return_value = handler1

        provider2 = Mock(spec=Provider)
        handler2 = Mock(spec=CommandHandler)
        provider2.return_value = handler2

        provider3 = Mock(spec=Provider)
        handler3 = Mock(spec=CommandHandler)
        provider3.return_value = handler3

        command = MockCommand("test_value")
        handlers = {MockCommand: (provider1, provider2, provider3)}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        mock_logger = mock_logger_manager.get_logger.return_value

        dispatcher.dispatch(command)

        mock_logger.info.assert_called_once_with(
            "Dispatching MockCommand to 3 handler(s)..."
        )

    def test_dispatch_handler_exception_propagates(self, mock_logger_manager, mock_handler_provider):
        """Test that exceptions from handlers are propagated."""
        provider, mock_handler = mock_handler_provider
        command = MockCommand("test_value")

        # Configure handler to raise an exception
        mock_handler.handle.side_effect = RuntimeError("Handler failed")

        handlers = {MockCommand: (provider,)}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        with pytest.raises(RuntimeError, match="Handler failed"):
            dispatcher.dispatch(command)

        mock_handler.handle.assert_called_once_with(command)

    def test_dispatch_different_command_types(self, mock_logger_manager):
        """Test dispatch with different command types."""
        class AnotherMockCommand(Command):
            def __init__(self, name: str):
                self.name = name

        # Set up handlers for different command types
        provider1 = Mock(spec=Provider)
        handler1 = Mock(spec=CommandHandler)
        provider1.return_value = handler1

        provider2 = Mock(spec=Provider)
        handler2 = Mock(spec=CommandHandler)
        provider2.return_value = handler2

        handlers = {
            MockCommand: (provider1,),
            AnotherMockCommand: (provider2,)
        }
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        # Dispatch first command type
        command1 = MockCommand("test")
        dispatcher.dispatch(command1)
        handler1.handle.assert_called_once_with(command1)
        handler2.handle.assert_not_called()

        # Reset mocks
        handler1.reset_mock()
        handler2.reset_mock()

        # Dispatch second command type
        command2 = AnotherMockCommand("another")
        dispatcher.dispatch(command2)
        handler1.handle.assert_not_called()
        handler2.handle.assert_called_once_with(command2)

    def test_dispatch_handler_creation_failure(self, mock_logger_manager):
        """Test behavior when handler provider fails to create handler."""
        provider = Mock(spec=Provider)
        provider.side_effect = Exception("Provider failed")

        command = MockCommand("test_value")
        handlers = {MockCommand: (provider,)}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        with pytest.raises(Exception, match="Provider failed"):
            dispatcher.dispatch(command)

    def test_dispatch_empty_handler_tuple(self, mock_logger_manager):
        """Test dispatch with empty handler tuple raises ValueError."""
        command = MockCommand("test_value")
        handlers = {MockCommand: ()}  # Empty tuple
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        # Empty tuple should be treated as no handlers registered
        with pytest.raises(ValueError, match="No handlers registered for command MockCommand"):
            dispatcher.dispatch(command)

    def test_dispatch_preserves_handler_execution_order(self, mock_logger_manager):
        """Test that handlers are executed in the order they appear in the tuple."""
        call_order = []

        def create_handler(name):
            handler = Mock(spec=CommandHandler)
            handler.handle.side_effect = lambda cmd: call_order.append(name)
            provider = Mock(spec=Provider)
            provider.return_value = handler
            return provider, handler

        provider1, handler1 = create_handler("handler1")
        provider2, handler2 = create_handler("handler2")
        provider3, handler3 = create_handler("handler3")

        command = MockCommand("test_value")
        handlers = {MockCommand: (provider1, provider2, provider3)}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        dispatcher.dispatch(command)

        assert call_order == ["handler1", "handler2", "handler3"]

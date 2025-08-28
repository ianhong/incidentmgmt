"""
Unit tests for the CommandDispatcher class.

This module contains comprehensive tests for the command dispatching functionality,
including success cases, error conditions, and mock verification to ensure
proper handler execution and logging behavior.
"""

import pytest
from unittest.mock import Mock, MagicMock, call
from typing import Type, Tuple

from application.commands.dispatcher import CommandDispatcher
from application.commands.base import Command, CommandHandler
from common.logger_manager import LoggerManager


class TestCommand(Command):
    """Test command class for testing purposes."""
    def __init__(self, data: str):
        self.data = data


class TestCommandHandler(CommandHandler[TestCommand]):
    """Test command handler for testing purposes."""
    
    def __init__(self):
        self.handle_called = False
        self.received_command = None
    
    def handle(self, command: TestCommand) -> None:
        """Handle the test command."""
        self.handle_called = True
        self.received_command = command


class AnotherTestCommand(Command):
    """Another test command class for testing multiple command types."""
    def __init__(self, value: int):
        self.value = value


class AnotherTestCommandHandler(CommandHandler[AnotherTestCommand]):
    """Handler for AnotherTestCommand."""
    
    def __init__(self):
        self.handle_called = False
    
    def handle(self, command: AnotherTestCommand) -> None:
        """Handle the another test command."""
        self.handle_called = True


class TestCommandDispatcher:
    """Test suite for CommandDispatcher class."""

    @pytest.fixture
    def mock_logger_manager(self):
        """Create a mock logger manager."""
        logger_manager = Mock(spec=LoggerManager)
        mock_logger = Mock()
        logger_manager.get_logger.return_value = mock_logger
        return logger_manager

    @pytest.fixture
    def mock_handler_provider(self):
        """Create a mock handler provider."""
        provider = Mock()
        handler = TestCommandHandler()
        provider.return_value = handler
        return provider, handler

    @pytest.fixture
    def dispatcher_with_single_handler(self, mock_logger_manager, mock_handler_provider):
        """Create a dispatcher with a single handler for TestCommand."""
        provider, handler = mock_handler_provider
        handlers = {
            TestCommand: (provider,)
        }
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        return dispatcher, provider, handler

    @pytest.fixture
    def dispatcher_with_multiple_handlers(self, mock_logger_manager):
        """Create a dispatcher with multiple handlers for the same command."""
        provider1 = Mock()
        handler1 = TestCommandHandler()
        provider1.return_value = handler1

        provider2 = Mock()
        handler2 = TestCommandHandler()
        provider2.return_value = handler2

        handlers = {
            TestCommand: (provider1, provider2)
        }
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        return dispatcher, [(provider1, handler1), (provider2, handler2)]

    def test_init_creates_logger_with_correct_name(self, mock_logger_manager):
        """Test that dispatcher initializes with correct logger name."""
        handlers = {}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        
        mock_logger_manager.get_logger.assert_called_once_with('application.commands.dispatcher')
        assert dispatcher._handlers == handlers

    def test_dispatch_single_handler_success(self, dispatcher_with_single_handler, mock_logger_manager):
        """Test successful dispatch to a single handler."""
        dispatcher, provider, handler = dispatcher_with_single_handler
        command = TestCommand("test data")
        mock_logger = mock_logger_manager.get_logger.return_value

        # Execute
        dispatcher.dispatch(command)

        # Verify
        provider.assert_called_once()
        assert handler.handle_called is True
        assert handler.received_command is command
        mock_logger.info.assert_called_once_with(
            "Dispatching TestCommand to 1 handler(s)..."
        )

    def test_dispatch_multiple_handlers_success(self, dispatcher_with_multiple_handlers, mock_logger_manager):
        """Test successful dispatch to multiple handlers."""
        dispatcher, handler_data = dispatcher_with_multiple_handlers
        command = TestCommand("test data")
        mock_logger = mock_logger_manager.get_logger.return_value

        # Execute
        dispatcher.dispatch(command)

        # Verify all providers were called
        for provider, handler in handler_data:
            provider.assert_called_once()
            assert handler.handle_called is True
            assert handler.received_command is command

        # Verify logging
        mock_logger.info.assert_called_once_with(
            "Dispatching TestCommand to 2 handler(s)..."
        )

    def test_dispatch_no_handlers_raises_value_error(self, mock_logger_manager):
        """Test that dispatch raises ValueError when no handlers are registered."""
        handlers = {}
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        command = TestCommand("test data")

        # Execute and verify
        with pytest.raises(ValueError) as exc_info:
            dispatcher.dispatch(command)

        assert "No handlers registered for command TestCommand" in str(exc_info.value)

    def test_dispatch_different_command_types(self, mock_logger_manager):
        """Test dispatch with different command types."""
        # Setup handlers for different command types
        test_provider = Mock()
        test_handler = TestCommandHandler()
        test_provider.return_value = test_handler

        another_provider = Mock()
        another_handler = AnotherTestCommandHandler()
        another_provider.return_value = another_handler

        handlers = {
            TestCommand: (test_provider,),
            AnotherTestCommand: (another_provider,)
        }
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)

        # Test TestCommand dispatch
        test_command = TestCommand("test")
        dispatcher.dispatch(test_command)
        
        test_provider.assert_called_once()
        assert test_handler.handle_called is True

        # Test AnotherTestCommand dispatch
        another_command = AnotherTestCommand(42)
        dispatcher.dispatch(another_command)
        
        another_provider.assert_called_once()
        assert another_handler.handle_called is True

    def test_dispatch_handler_exception_propagates(self, mock_logger_manager):
        """Test that exceptions from handlers are propagated."""
        # Setup handler that raises exception
        provider = Mock()
        handler = Mock()
        handler.handle.side_effect = RuntimeError("Handler error")
        provider.return_value = handler

        handlers = {
            TestCommand: (provider,)
        }
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        command = TestCommand("test")

        # Execute and verify exception propagates
        with pytest.raises(RuntimeError) as exc_info:
            dispatcher.dispatch(command)

        assert "Handler error" in str(exc_info.value)
        provider.assert_called_once()
        handler.handle.assert_called_once_with(command)

    def test_dispatch_multiple_handlers_first_fails_second_not_called(self, mock_logger_manager):
        """Test that if first handler fails, subsequent handlers are not called."""
        # Setup first handler that fails
        provider1 = Mock()
        handler1 = Mock()
        handler1.handle.side_effect = RuntimeError("First handler error")
        provider1.return_value = handler1

        # Setup second handler
        provider2 = Mock()
        handler2 = Mock()
        provider2.return_value = handler2

        handlers = {
            TestCommand: (provider1, provider2)
        }
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        command = TestCommand("test")

        # Execute and verify
        with pytest.raises(RuntimeError):
            dispatcher.dispatch(command)

        # First handler should be called
        provider1.assert_called_once()
        handler1.handle.assert_called_once_with(command)

        # Second handler should not be called
        provider2.assert_not_called()
        handler2.handle.assert_not_called()

    def test_dispatch_logs_correct_handler_count(self, mock_logger_manager):
        """Test that logging shows correct handler count for different scenarios."""
        mock_logger = mock_logger_manager.get_logger.return_value

        # Test with 3 handlers
        providers = []
        for i in range(3):
            provider = Mock()
            handler = TestCommandHandler()
            provider.return_value = handler
            providers.append(provider)

        handlers = {
            TestCommand: tuple(providers)
        }
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        command = TestCommand("test")

        dispatcher.dispatch(command)

        mock_logger.info.assert_called_once_with(
            "Dispatching TestCommand to 3 handler(s)..."
        )

    def test_handlers_dictionary_is_stored_correctly(self, mock_logger_manager):
        """Test that the handlers dictionary is stored as provided."""
        provider = Mock()
        handlers = {
            TestCommand: (provider,),
            AnotherTestCommand: (provider,)
        }
        
        dispatcher = CommandDispatcher(mock_logger_manager, handlers)
        
        assert dispatcher._handlers is handlers
        assert len(dispatcher._handlers) == 2
        assert TestCommand in dispatcher._handlers
        assert AnotherTestCommand in dispatcher._handlers

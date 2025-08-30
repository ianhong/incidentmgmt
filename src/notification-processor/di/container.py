"""
Dependency Injection Container Module
"""

from dependency_injector import containers, providers
from application.commands.create_incident import (
    CreateIncidentCommand,
    CreateIncidentCommandHandler,
)
from application.commands.dispatcher import CommandDispatcher
from application.commands.factory import CommandFactory
from config.config_manager import ConfigManager
from common.logger_manager import LoggerManager

class Container(containers.DeclarativeContainer):
    """
    Dependency injection container for the notification processor.
    """
    logger_manager = providers.Singleton(
        LoggerManager,
    )

    config_manager = providers.Singleton(
        ConfigManager,
        logger_manager=logger_manager,
    )

    create_incident_handler = providers.Factory(
        CreateIncidentCommandHandler,
        config_manager=config_manager,
        logger_manager=logger_manager
    )

    command_factory = providers.Singleton(
        CommandFactory,
    )

    command_dispatcher = providers.Factory(
        CommandDispatcher,
        logger_manager=logger_manager,
        handlers=providers.Dict(
            {
                CreateIncidentCommand: (
                    create_incident_handler,
                ),
            }
        ),
    )

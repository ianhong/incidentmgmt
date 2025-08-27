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
    create_incident_handler = providers.Factory(CreateIncidentCommandHandler)

    config_manager = providers.Singleton(
        ConfigManager,
    )

    log_manager = providers.Singleton(
        LoggerManager,
        config_manager=config_manager,
    )

    command_factory = providers.Singleton(
        CommandFactory,
    )
    command_dispatcher = providers.Factory(
        CommandDispatcher,
        handlers=providers.Dict(
            {
                CreateIncidentCommand: (
                    create_incident_handler,
                ),
            }
        ),
    )
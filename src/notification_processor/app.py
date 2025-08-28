#!/usr/bin/env python3
"""
Incident Management Notification Processor
"""

import argparse
import asyncio
from functools import partial
import os
import signal
from di.container import Container
from infra.subscriber import Subscriber

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
logger = None


def handle_shutdown(shutdown_event):
    """
    Handle shutdown signals by setting the shutdown event.

    Args:
        shutdown_event: asyncio.Event to signal shutdown to the main loop
    """
    global logger
    logger.warning("Received shutdown signal. Shutting down gracefully...")
    if shutdown_event:
        shutdown_event.set()


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parse = argparse.ArgumentParser(
        description="Incident Management Notification Service"
    )
    parse.add_argument("--config")
    return parse.parse_args()


async def main():
    """
    Main application entry point.
    """
    global logger

    container = Container()
    config_manager = container.config_manager()
    logging_manager = container.logger_manager()

    args = parse_arguments()

    config = config_manager.load_config(args.config)

    logger = logging_manager.get_logger(__name__)

    subscriber = Subscriber(
        project_id=config.get("project_id"),
        subscription_id=config.get("subscription_id"),
        container=container,
        max_messages=config.get("max_messages"),
    )

    shutdown_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(
                sig, partial(handle_shutdown, shutdown_event=shutdown_event)
            )
        except NotImplementedError:
            pass
    subscriber_task = asyncio.create_task(subscriber.run_subscriber())
    await shutdown_event.wait()
    subscriber_task.cancel()
    try:
        await subscriber_task
    except asyncio.CancelledError:
        logger.error("Subscriber task cancelled.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)

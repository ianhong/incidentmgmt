#!/usr/bin/env python3

import argparse
import asyncio
from functools import partial
import os
import signal
from config.container import Container
from config.config_manager import ConfigManager
from infra.subscriber import Subscriber

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def handle_shutdown(shutdown_event):
    print("\n🛑 Received shutdown signal. Shutting down gracefully...")
    if shutdown_event:
        shutdown_event.set()

def parse_arguments():
    parse = argparse.ArgumentParser(description="Incident Management Notification Service")
    parse.add_argument("--config")
    return parse.parse_args()

async def main():
    args = parse_arguments()

    container = Container()

    config_manager = container.config_manager()
    config = config_manager.load_config(args.config)

    subscriber = Subscriber(
        project_id=config.get("project_id"),
        subscription_id=config.get("subscription_id"),
        container=container,
        max_messages=config.get("max_messages")
    )

    shutdown_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(
                sig,
                partial(handle_shutdown, shutdown_event=shutdown_event)
            )
        except NotImplementedError:
            pass
    subscriber_task = asyncio.create_task(subscriber.run_subscriber())
    await shutdown_event.wait()
    subscriber_task.cancel()
    try:
        await subscriber_task
    except asyncio.CancelledError:
        print("Subscriber task cancelled.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        exit(1)

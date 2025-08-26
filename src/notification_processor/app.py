#!/usr/bin/env python3

import asyncio
from functools import partial
import os
import signal
from config.container import Container
from infra.subscriber import Subscriber

# Configuration from environment variables
PROJECT_ID = os.environ.get("PUBSUB_PROJECT_ID", "local-project")
TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID", "my-topic")
SUBSCRIPTION_ID = "my-sub"

# Thread pool for bridging sync/async
container = Container()
subscriber = Subscriber(
    project_id=PROJECT_ID,
    subscription_id=SUBSCRIPTION_ID,
    container=container,
    max_messages=100
)

def handle_shutdown(shutdown_event):
    print("\n🛑 Received shutdown signal. Shutting down gracefully...")
    if shutdown_event:
        shutdown_event.set()

async def main():
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

#!/usr/bin/env python3

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from google.cloud import pubsub_v1
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

async def main():
    await asyncio.gather(
        subscriber.run_subscriber()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        exit(1)

#!/usr/bin/env python3

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from google.cloud import pubsub_v1

# Configuration from environment variables
PROJECT_ID = os.environ.get("PUBSUB_PROJECT_ID", "local-project")
TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID", "my-topic")
SUBSCRIPTION_ID = "my-sub"

# Thread pool for bridging sync/async
executor = ThreadPoolExecutor(max_workers=4)

async def async_process_message(message):
    """
    Async function to process a message.
    This is where you'll add your async logic later.
    """
    try:
        message_data = message.data.decode('utf-8')
        print(f"📨 Async processing message: {message_data}")
        data = json.loads(message_data)
        command = data.get('command')

        # Command handler registry
        async def handle_ping(data):
            print("🏓 Received ping command")
            await asyncio.sleep(0.05)
            print("🏓 Pong!")
            return True

        async def handle_echo(data):
            print(f"🔊 Echo: {data.get('payload')}")
            await asyncio.sleep(0.05)
            return True

        handlers = {
            'ping': handle_ping,
            'echo': handle_echo,
        }

        handler = handlers.get(command)
        if handler:
            result = await handler(data)
            print(f"✅ Command '{command}' processed for message: {message.message_id}")
            return result
        else:
            print(f"⚠️ Unknown command: {command}")
            return False
    except Exception as e:
        print(f"❌ Error processing message {getattr(message, 'message_id', '?')}: {e}")
        return False

def sync_callback(message):
    """
    Sync callback that bridges to async processing.
    This is called by the Pub/Sub client.
    """
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        success = loop.run_until_complete(async_process_message(message))
        if success:
            message.ack()
            print(f"✅ Acknowledged message: {message.message_id}")
        else:
            message.nack()
            print(f"❌ Nacked message: {message.message_id}")
    except Exception as e:
        print(f"💥 Error in callback for message {message.message_id}: {e}")
        message.nack()

def main():
    """Main function using future-based (blocking) pattern."""
    print("🚀 Starting Pub/Sub Subscriber")
    print(f"📋 Project: {PROJECT_ID}")
    print(f"📋 Subscription: {SUBSCRIPTION_ID}")

    # Create subscriber client
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    print(f"🎧 Listening for messages on {subscription_path}...")
    print("Press Ctrl+C to stop...")

    # Configure flow control
    flow_control = pubsub_v1.types.FlowControl(max_messages=100)

    # Start the subscriber with our sync callback that bridges to async
    subscriber_future = subscriber.subscribe(
        subscription_path,
        callback=sync_callback,
        flow_control=flow_control
    )

    try:
        # Block on the future result (handles messages until stopped)
        subscriber_future.result()
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal, shutting down...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Clean shutdown
        subscriber_future.cancel()
        try:
            subscriber_future.result()
        except Exception as e:
            print(f"Warning during shutdown: {e}")

        subscriber.close()
        executor.shutdown(wait=True)
        print("🔒 Subscriber closed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        exit(1)

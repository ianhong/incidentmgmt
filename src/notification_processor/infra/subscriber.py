import asyncio
from google.cloud.pubsub_v1 import SubscriberClient
from google.cloud.pubsub_v1.types import FlowControl
from config.container import Container

class Subscriber:
    def __init__(self, project_id: str, subscription_id: str, container: Container, max_messages: int):
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.max_messages = max_messages
        self.container = container
        self.subscriber = SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(project_id, subscription_id)

    async def run_subscriber(self):
        """Main function using future-based (blocking) pattern."""
        print("🚀 Starting Pub/Sub Subscriber")
        print(f"📋 Project: {self.project_id}")
        print(f"📋 Subscription: {self.subscription_id}")

        print(f"🎧 Listening for messages on {self.subscription_path}...")
        print("Press Ctrl+C to stop...")

        # Define the callback here to capture self/container
        def sync_callback(message):
            """
            Sync callback that bridges to async processing.
            This is called by the Pub/Sub client.
            """
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.async_process_message(message))
                if success:
                    message.ack()
                    print(f"✅ Acknowledged message: {message.message_id}")
                else:
                    message.nack()
                    print(f"❌ Nacked message: {message.message_id}")
            except Exception as e:
                print(f"💥 Error in callback for message {message.message_id}: {e}")
                message.nack()

        # Configure flow control
        flow_control = FlowControl(max_messages=100)

        # Start the subscriber with our sync callback that bridges to async
        subscriber_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=sync_callback,
            flow_control=flow_control
        )

        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, subscriber_future.result)
        except asyncio.CancelledError:
            print("🛑 Subscriber task cancelled.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            subscriber_future.cancel()
            self.subscriber.close()
            print("🔒 Subscriber closed")
    
    async def async_process_message(self, message):
        """
        Async function to process a message.
        This is where you'll add your async logic later.
        """
        try:
            command_dispatcher = self.container.command_dispatcher()
            command_factory = self.container.command_factory()
            command = command_factory.create(message)
            command_dispatcher.dispatch(command)

            print(f"✅ Message processed: {message.message_id}")
            return True
        except Exception as e:
            print(f"❌ Error processing message {message.message_id}: {e}")
            return False

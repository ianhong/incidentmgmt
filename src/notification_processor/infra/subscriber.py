"""
Google Cloud Pub/Sub Subscriber Infrastructure Module
"""

import asyncio
from google.cloud.pubsub_v1 import SubscriberClient
from google.cloud.pubsub_v1.types import FlowControl
from config.container import Container

class Subscriber:
    """
    Google Cloud Pub/Sub subscriber for processing incident management messages.
    """

    def __init__(self, project_id: str, subscription_id: str, container: Container, max_messages: int):
        """
        Initialize the Pub/Sub subscriber.

        Args:
            project_id: Google Cloud project ID
            subscription_id: Pub/Sub subscription ID
            container: Dependency injection container
            max_messages: Maximum number of messages to process concurrently
        """
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.max_messages = max_messages
        self.container = container
        self.subscriber = SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(project_id, subscription_id)
        self.logger = container.logger_manager().get_logger(__name__)

    async def run_subscriber(self):
        """
        Main subscriber method using future-based (blocking) pattern.
        """
        self.logger.info("Starting Pub/Sub Subscriber")
        self.logger.info(f"Project: {self.project_id}")
        self.logger.info(f"Subscription: {self.subscription_id}")
        self.logger.info(f"Listening for messages on {self.subscription_path}...")

        # Define the callback here to capture self/container
        def sync_callback(message):
            """
            Synchronous callback that bridges to async processing.

            Args:
                message: Pub/Sub message to process
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
                    self.logger.debug(f"Acknowledged message: {message.message_id}")
                else:
                    message.nack()
                    self.logger.debug(f"Nacked message: {message.message_id}")
            except Exception as e:
                self.logger.error(f"Error in callback for message {message.message_id}: {e}")
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
            self.logger.warning("Subscriber task cancelled.")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            subscriber_future.cancel()
            self.subscriber.close()
            self.logger.info("Subscriber closed")

    async def async_process_message(self, message):
        """
        Asynchronously process a received Pub/Sub message.

        Args:
            message: Pub/Sub message to process

        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            command_dispatcher = self.container.command_dispatcher()
            command_factory = self.container.command_factory()
            command = command_factory.create(message)
            command_dispatcher.dispatch(command)

            self.logger.debug(f"Message processed: {message.message_id}")
            return True
        except Exception as e:
            self.logger.debug(f"Error processing message {message.message_id}: {e}")
            return False

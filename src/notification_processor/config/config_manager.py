import os
import json

class ConfigManager:
    """
    Centralized configuration manager for environment variables and settings.
    """
    def __init__(self):
        config = {}
        self.project_id = os.environ.get("PUBSUB_PROJECT_ID", "unknown")
        self.topic_id = os.environ.get("PUBSUB_TOPIC_ID", "unkonwn")
        self.subscription_id = os.environ.get("PUBSUB_SUBSCRIPTION_ID", "unknown")
        self.max_messages = int(os.environ.get("PUBSUB_MAX_MESSAGES", "100"))
        self.log_level = os.environ.get("PUBSUB_LOG_LEVEL", "WARNING")

    def load_config(self, config_path=None):
        if not config_path:
            return self._as_dict()
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load config file {config_path}: {e}")
            return {}

    def _as_dict(self):
        return {
            "project_id": self.project_id,
            "topic_id": self.topic_id,
            "subscription_id": self.subscription_id,
            "max_messages": self.max_messages,
            "log_level": self.log_level
        }

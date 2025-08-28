# Build the image
docker build -t notification-processor /Users/ihong/src/incident-mgmt-poc/src/notification_processor/

# Run the container
docker run --rm notification-processor

# Run with custom config
docker run --rm -v /path/to/config:/app/config notification-processor --config config/custom-config.json


docker run --rm --network host \
  -e PUBSUB_PROJECT_ID=local-project \
  -e PUBSUB_SUBSCRIPTION_ID=my-sub \
  -e PUBSUB_LOG_LEVEL=INFO \
  -e PUBSUB_EMULATOR_HOST=localhost:8681 \
  notification-processor


PUBSUB_PROJECT_ID=local-project
PUBSUB_TOPIC_ID=my-topic
PUBSUB_SUBSCRIPTION_ID=my-sub
PUBSUB_MAX_MESSAGES=100
PUBSUB_LOG_LEVEL=INFO
PUBSUB_LOG_FORMAT=json

export PUBSUB_PROJECT_ID=local-project
export PUBSUB_TOPIC_ID=my-topic
export PUBSUB_SUBSCRIPTION_ID=my-sub
export PUBSUB_MAX_MESSAGES=100
export PUBSUB_LOG_LEVEL=INFO
export PUBSUB_LOG_FORMAT=json

# Incident Management Notification Processor

A robust, production-ready notification processing service built with Python that handles Google Cloud Pub/Sub messages for incident management workflows. The service is designed using Clean Architecture principles with dependency injection, structured logging, and graceful shutdown capabilities for Kubernetes deployments.

## Purpose

The notification processor serves as a critical component in an incident management system, responsible for:

- **Message Processing**: Consuming incident-related notifications from Google Cloud Pub/Sub
- **Command Handling**: Converting raw messages into structured commands using the Command pattern
- **Incident Management**: Processing various incident lifecycle events (creation, updates, resolution)
- **Reliable Processing**: Ensuring message acknowledgment/negative acknowledgment for fault tolerance
- **Observability**: Providing structured logging with enriched context for monitoring and debugging

## Architecture Overview

The service follows **Clean Architecture** principles with clear separation of concerns:

```
├── app.py                    # Application entry point
├── application/              # Business logic layer
├── config/                   # Configuration and DI
├── common/                   # Cross-cutting concerns
└── infra/                    # Infrastructure layer
```

## Package Descriptions

### `application/commands/`
**Business Logic Layer** - Contains the core business logic for processing commands:
- **`base.py`**: Abstract base classes for Command pattern implementation
- **`create_incident.py`**: Command and handler for creating new incidents
- **`factory.py`**: Factory for creating command objects from raw message payloads
- **`dispatcher.py`**: Routes commands to their appropriate handlers

### `config/`
**Configuration Layer** - Manages application configuration and dependency injection:
- **`config_manager.py`**: Centralized configuration management from environment variables and JSON files
- **`container.py`**: Dependency injection container using dependency-injector framework

### `common/`
**Cross-Cutting Concerns** - Shared utilities used across application layers:
- **`logger_manager.py`**: Structured logging with enriched context using structlog

### `infra/`
**Infrastructure Layer** - External service integrations and I/O operations:
- **`subscriber.py`**: Google Cloud Pub/Sub subscriber implementation with async message processing

## Design Patterns

### 1. **Command Pattern**
- **Purpose**: Encapsulates requests as objects, enabling loose coupling between request and execution
- **Implementation**: `Command` base class, concrete commands like `CreateIncidentCommand`, and corresponding handlers
- **Benefits**: Easy to extend with new command types, supports undo operations, and enables queuing

### 2. **Factory Pattern**
- **Purpose**: Creates command objects from raw message payloads without exposing instantiation logic
- **Implementation**: `CommandFactory` class that maps message types to command classes
- **Benefits**: Centralized object creation, easy to extend with new command types

### 3. **Dependency Injection**
- **Purpose**: Manages dependencies and promotes loose coupling between components
- **Implementation**: `dependency-injector` framework with `Container` class
- **Benefits**: Improved testability, flexibility, and maintainability

### 4. **Repository Pattern** (Future)
- **Purpose**: Abstracts data access logic for incident persistence
- **Status**: Prepared for implementation when data persistence is added

## Cross-Cutting Concerns

### 1. **Logging**
- **Implementation**: Structured logging with `structlog`
- **Features**: 
  - JSON and console output formats
  - Enriched context (process ID, thread ID, hostname, application metadata)
  - Exception handling with full stack traces
  - Configurable log levels via environment variables

### 2. **Configuration Management**
- **Implementation**: Centralized configuration with fallback hierarchy
- **Sources**: Environment variables → JSON files → defaults
- **Features**: 
  - Runtime configuration loading
  - Environment-specific settings
  - Validation and error handling

### 3. **Error Handling**
- **Implementation**: Comprehensive exception handling throughout the application
- **Features**:
  - Graceful degradation
  - Proper message acknowledgment/negative acknowledgment
  - Structured error logging with context

### 4. **Signal Handling**
- **Implementation**: Graceful shutdown on SIGINT/SIGTERM
- **Features**:
  - Clean resource cleanup
  - Proper task cancellation
  - Kubernetes-friendly shutdown behavior

### 5. **Observability**
- **Implementation**: Structured logging with correlation IDs and metrics
- **Features**:
  - Request tracing
  - Performance monitoring
  - Health checks (future)

## Getting Started

### Prerequisites
- Python 3.8+
- Google Cloud SDK configured
- Pub/Sub topic and subscription created

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
Set environment variables or create a config.json file:
```bash
export PUBSUB_PROJECT_ID="your-project-id"
export PUBSUB_SUBSCRIPTION_ID="your-subscription"
export PUBSUB_LOG_LEVEL="INFO"
export PUBSUB_LOG_FORMAT="json"  # or "console"
```

### Running the Service
```bash
python app.py --config config.json
```

## Kubernetes Deployment

The service is designed for containerized deployment with:
- Graceful shutdown handling
- Structured JSON logging for log aggregation
- Environment-based configuration
- Health check endpoints (future)
- Resource limits and requests

## Development

### Adding New Commands
1. Create command class inheriting from `Command`
2. Create corresponding handler inheriting from `CommandHandler`
3. Register in `CommandFactory`
4. Add to dependency injection container

### Testing
```bash
# Run tests (when implemented)
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Future Enhancements

- Health check endpoints
- Metrics collection (Prometheus)
- Circuit breaker pattern
- Retry mechanisms with exponential backoff
- Dead letter queue handling
- Database integration with Repository pattern
- API endpoints for status and management

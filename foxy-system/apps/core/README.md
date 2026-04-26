# Foxy Core

`core` contains code shared by `collector`, `processor`, and the future HTTP API.

The current console modules still keep compatibility wrappers in their original
locations, for example:

- `collector/base_class/os_env_geral.py`
- `processor/base_class/os_env_geral.py`
- `collector/custom_event.py`
- `processor/custom_event.py`
- `collector/api/gateway/rabbitmq_env.py`
- `processor/api/gateway/rabbitmq_env.py`

Those wrappers should stay small and import from `core`. New shared behavior
should be added here first, then consumed by the console modules and the API.

Current shared modules:

- `environment.py`: general environment variables loaded from `/apps/config`.
- `source_mode.py`: common source mode enum.
- `events.py`: console key event primitives.
- `rabbitmq_env.py`: RabbitMQ queue/routing-key naming and management API helper.


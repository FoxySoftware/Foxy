import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from core.environment import OsEnvGeneral as Env


COLLECTOR_MODULE_SOURCE = "collector"
PROCESSOR_MODULE_SOURCE = "processor"


class RabbitMqEnv:
    def __init__(self, host, username, password, port, exchange_name, vhost="/"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._vhost = vhost
        self.exchange_name = exchange_name
        self.vhost_encoded = urllib.parse.quote(self._vhost, safe="")
        self.exchange_name_encoded = urllib.parse.quote(exchange_name, safe="")
        self.url = (
            f"http://{host}:{port}/api/exchanges/"
            f"{self.vhost_encoded}/{self.exchange_name_encoded}/bindings/source"
        )

    def get_list_routing_keys(
        self,
        filter_project_name: str = None,
        filter_module_source: str = None,
    ) -> list[str] | Exception:
        if filter_project_name is not None:
            filter_project_name = filter_project_name.lower()

        response = requests.get(self.url, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve bindings: {response.status_code} - {response.text}")

        bindings = response.json()
        routing_keys = {binding["routing_key"] for binding in bindings}
        if filter_project_name is not None:
            routing_keys = [key for key in routing_keys if filter_project_name in key]
        if filter_module_source is not None:
            routing_keys = [key for key in routing_keys if filter_module_source in key]
        return routing_keys

    @staticmethod
    def get_queue_name(filter_module_source: str, screen_id: str) -> str:
        if not screen_id:
            raise Exception("Session id required")
        if COLLECTOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_QUEUE_PREFIX_COLLECTOR.value}_{screen_id}"
        if PROCESSOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_QUEUE_PREFIX_PROCESSOR.value}_{screen_id}"
        raise Exception(f"Unknown RabbitMQ module source: {filter_module_source}")

    @staticmethod
    def get_routing_key_name(filter_module_source: str, screen_id: str) -> str:
        if not screen_id:
            raise Exception("Session id required")
        if COLLECTOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_PREFIX_ROUTING_KEY_COLLECTOR.value}_{screen_id}"
        if PROCESSOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_PREFIX_ROUTING_KEY_PROCESSOR.value}_{screen_id}"
        raise Exception(f"Unknown RabbitMQ module source: {filter_module_source}")


import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
from processor.base_class.os_env_geral import OsEnvGeneral as Env


COLLECTOR_MODULE_SOURCE = "collector"
PROCESSOR_MODULE_SOURCE = "processor"

class RabbitMqEnv():

    """
     COLLECTOR RABBIT FORMAT 
     session_id = "0_zgh_19-08-2024_ift4_starship_web"
     prefix_queue = "queue_collector"
     prefix_routing_key = "routing_key_collector"
     queue=f"{prefix_queue}_{session_id}"
     routing_key=f"{prefix_routing_key}_{session_id}"
     
    """
  
    def __init__(self,  host, username, password, port, exchange_name, vhost="/"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._vhost = vhost  # The virtual host, check en web rabbitmq panel section admin. 
        self.exchange_name = exchange_name        
        self.vhost_encoded = urllib.parse.quote(self._vhost, safe='')
        self.exchange_name_encoded = urllib.parse.quote(exchange_name, safe='')
        self.url = f'http://{host}:{port}/api/exchanges/{self.vhost_encoded}/{self.exchange_name_encoded}/bindings/source'
    
    def get_list_routing_keys(self, filter_project_name:str=None, filter_module_source:str = None) -> list[str] | Exception  :
        response = requests.get(self.url, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            bindings = response.json()
            routing_keys = {binding['routing_key'] for binding in bindings}
            if filter_project_name is not None:
                routing_keys = [key for key in routing_keys if filter_project_name in key]
            if filter_module_source is not None:
                routing_keys = [key for key in routing_keys if filter_module_source in key]
            return routing_keys
        else:
            raise Exception(f"Failed to retrieve bindings: {response.status_code} - {response.text}")
        
    @staticmethod
    def get_queue_name(filter_module_source:str ,screen_id:str ) -> str:
        if not screen_id:
            raise Exception("Session id required")
        if COLLECTOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_QUEUE_PREFIX_COLLECTOR.value}_{screen_id}"
        if PROCESSOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_QUEUE_PREFIX_PROCESSOR.value}_{screen_id}"
    
    @staticmethod
    def get_routing_key_name( filter_module_source:str ,screen_id:str ) -> str:
        if not screen_id:
            raise Exception("Session id required")
        if COLLECTOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_PREFIX_ROUTING_KEY_COLLECTOR.value}_{screen_id}"
        if PROCESSOR_MODULE_SOURCE in filter_module_source:
            return f"{Env.RABBITMQ_PREFIX_ROUTING_KEY_PROCESSOR.value}_{screen_id}"

    

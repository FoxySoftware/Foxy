import os
from enum import Enum
from pathlib import Path

class Mode(Enum):
    WRITE:str = "WRITE"
    READ:str = "READ"
    
    
CURRENT_MODE = Mode.READ

current_dir = Path(__file__).parent
PATH_CONFIG_FILE = current_dir / '../../config/os_general.env'
PATH_CONFIG_FILE = PATH_CONFIG_FILE.resolve()


class OsEnvGeneral(Enum):
    # These four come from beyond. ! is not in default. 
    OS_HOST:str = "HOST_OS"
    FOXY_PATH:str = "FOXY_PATH"
    UID:str = "UID"
    GID:str = "GID"

    
    NAME_FILE_SETTINGS:str = "NAME_FILE_SETTINGS"
    NAME_FILE_SETTING_AREAS:str = "NAME_FILE_SETTING_AREAS"
    RABBITMQ_USERNAME:str = "RABBITMQ_USERNAME"
    RABBITMQ_PASSSWORD:str = "RABBITMQ_PASSSWORD"
    RABBITMQ_HOST:str = "RABBITMQ_HOST"
    RABBITMQ_PORT:str = "RABBITMQ_PORT"
    RABBITMQ_QUEUE_PREFIX_COLLECTOR:str = "RABBITMQ_QUEUE_PREFIX_COLLECTOR"
    RABBITMQ_QUEUE_PREFIX_PROCESSOR:str = "RABBITMQ_QUEUE_PREFIX_PROCESSOR"
    RABBITMQ_PREFIX_ROUTING_KEY_COLLECTOR:str = "RABBITMQ_PREFIX_ROUTING_KEY_COLLECTOR"
    RABBITMQ_PREFIX_ROUTING_KEY_PROCESSOR:str = "RABBITMQ_PREFIX_ROUTING_KEY_PROCESSOR"
    RABBITMQ_EXCHANGE:str = "RABBITMQ_EXCHANGE"


    @classmethod
    def set_as_environment_variables_from_file(cls):

        try:
            with open(PATH_CONFIG_FILE, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        os.environ[key] = value
        except FileNotFoundError:
            raise Exception("Create ENV file first !")

    @classmethod
    def create_file_env(cls):

        with open(PATH_CONFIG_FILE, 'w') as file:
            for env_var in OsEnvGeneral:
                try:
                    _default[env_var.name]
                    file.write(f"{env_var.name}={_default[env_var.name].value}\n")
                except:
                    # IGNORE OS_HOST and FOXY_PATH
                    pass
    @classmethod
    def list_environment_variables(cls):
        for key, value in os.environ.items():
            print(f"{key}={value}")

    @property
    def value(self):        
        return os.environ.get(self.name, None)

class _default(Enum):

    NAME_FILE_SETTINGS = "settings.ini"
    NAME_FILE_SETTING_AREAS = "setting_areas.ini"
    RABBITMQ_USERNAME = 'admin'
    RABBITMQ_PASSSWORD = 'pass'
    RABBITMQ_HOST = 'rabbitmq'
    RABBITMQ_PORT = '15672'
    RABBITMQ_QUEUE_PREFIX_COLLECTOR =  'queue_collector'
    RABBITMQ_QUEUE_PREFIX_PROCESSOR = 'queue_processor'
    RABBITMQ_PREFIX_ROUTING_KEY_COLLECTOR ='routing_key_collector'
    RABBITMQ_PREFIX_ROUTING_KEY_PROCESSOR = 'queue_processor'
    RABBITMQ_EXCHANGE = 'exchange_direct_foxy'
    
    

if __name__ == "__main__":
    if CURRENT_MODE == Mode.READ:
        OsEnvGeneral.set_as_environment_variables_from_file()
        OsEnvGeneral.list_environment_variables()
    elif CURRENT_MODE == Mode.WRITE:
        OsEnvGeneral.create_file_env()
        OsEnvGeneral.set_as_environment_variables_from_file()
        OsEnvGeneral.list_environment_variables()

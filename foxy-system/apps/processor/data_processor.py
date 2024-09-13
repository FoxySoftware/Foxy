import json
import re
import threading
import time
from types import NoneType
from api.gateway.rabbitmq_env import  PROCESSOR_MODULE_SOURCE, RabbitMqEnv
from base_class.area_ocr_model import AreaOcrModel, AreaType
from base_class.data_processor_enums import (AvoidUnpackKeysToT2, 
                                  AvoidUnpackKeysToTX,
                                  DataStructureVar,
                                  SqlType,
                                  TxDualIndex, 
                                  TxThirdIndexDimension, StructureType,
                                  UnpackKeysToT2, 
                                  UnpackKeysToTX)
from data_structure import DataStructure
from folder_manager import FolderManager
from processor.base_class.os_env_processor_folders import EnvFolders
from resource_processor.utils_decorators import CounterLog
from base_class.shared_keys import SharedKeys
from api.gateway.rabbitmq import RabbitMQ
from api.services.handler import Handler
from typing import TYPE_CHECKING
from processor.base_class.os_env_geral import OsEnvGeneral as Env
from rich.progress import Progress, TaskID



if TYPE_CHECKING:
    from settings_manager import SettingManager


ct_log:CounterLog = CounterLog(print_message=False)

class DataProcessor(RabbitMQ, DataStructure):
    
    
    T1_NAME = "PROJECT"
    T2_NAME = "COLLECTOR"
    
    #no optionals
    key_area_value = SharedKeys.KEY_AREA_VALUE.value # in tx×
    key_area_name = SharedKeys.KEY_AREA_NAME.value # in tx×
    key_area_group = SharedKeys.KEY_AREA_GROUP.value # in tx×
    #optionals
    key_area_number = SharedKeys.KEY_AREA_NUMBER.value # in tx×
    key_area_raw_value = SharedKeys.KEY_AREA_RAW_VALUE.value # in tx×
    key_area_path_image = SharedKeys.KEY_AREA_PATH_IMAGE.value # in tx×
    
    key_screen_id = SharedKeys.KEY_SCREEN_ID.value # 
    key_image_screenshot_name = SharedKeys.KEY_IMAGE_SCREENSHOT_NAME.value #foreign  key t2 -> tx×
    key_image_screenshot_link = SharedKeys.KEY_IMAGE_SCREENSHOT_LINK.value
    key_collector_data = SharedKeys.KEY_COLLECTOR_DATA.value #key to unpack in t2  
    key_areas_ocr = SharedKeys.KEY_AREAS_OCR.value # key where is list_dict_tx
    #PropertyCaptureSession
    #no optional en collector(t2) table, but optional in (tx×)
    key_session_id = SharedKeys.KEY_SESSION_ID.value  # 'session_id' as foreign in tx
    key_session_code = SharedKeys.KEY_SESSION_CODE.value  # 'session_code'
    key_is_start_session = SharedKeys.KEY_IS_START_SESSION.value  # 'is_start_session'
    key_is_end_session = SharedKeys.KEY_IS_END_SESSION.value  # 'is_end_session'
    key_is_change_detected = SharedKeys.KEY_IS_CHANGE_DETECTED.value  # 'is_change_detected'
    key_timestamp_seconds = SharedKeys.KEY_TIMESTAMP_SECONDS.value  # 'timestamp_seconds'
    key_session_captures_number = SharedKeys.KEY_SESSION_CAPTURES_NUMBER.value  # 'session_captures_number'
    key_date = SharedKeys.KEY_DATE.value  # 'date'
        
    

    def __init__(self, **kwargs):
        super().__init__( **kwargs)
        self.project_name = kwargs["project_name"]
        self.screen_id:str = kwargs["screen_id"]
        self.current_language:str = kwargs.get("current_language", "EN")
        self.available_language:dict[str,str] = kwargs["available_language"]
        
        self.stop_event:threading.Event = kwargs.get("stop_event",  threading.Event())
        self._folder_manager:callable = kwargs["folder_manager"]
        self._setting_manager:callable = kwargs["setting_manager"]
        self._rabbit_processor:Handler | None = None
        self._total_processed:int = 0
        self._message:str | None = None
        self._error_message:str | None  = None
        
        self._0_t1_primary_key:str =  self.key_screen_id
        self._1_t1_key_name:str = "project_name"
        self._2_t1_key_source:str = "source"
        self._3_t1_key_source_type:str = "source_type"
        self._4_t1_key_resolution:str = "source_resolution"


    @property
    def folder_manager(self)-> FolderManager:
        return self._folder_manager()

    @property
    def setting_manager(self) -> 'SettingManager': 
        return self._setting_manager()
    
    @property
    def rabbit_processor(self) -> Handler: 
        if  self._rabbit_processor is None:
            self.__init_rabbit_processor_handler()
        return self._rabbit_processor
    


    def get_current_task_properties(self) -> dict[str, str] | None:

        if isinstance(self._error_message, str):
            if data_dict:
                data_dict["error_message"] = self._error_message
            else:
                data_dict= {"error_message": self._error_message}
        
        if isinstance(self._message, str):
            if data_dict:
                data_dict["message"] = self._message
            else:
                data_dict= {"message": self._message}
                
        return data_dict
    
    def purge_queue_processed(self, option_str):
        with Progress() as progress:
            task_id:TaskID = progress.add_task(f"[cyan]{option_str}", total=2)
            self.start_server()
            time.sleep(.5)
            progress.update(task_id, advance=1)
            self.__get_queue_data_processor()
            progress.update(task_id, advance=1)

    def start_data_export_database(self,
                                   db_name,
                                   dict_tx_options:dict[str,list[str]],
                                   option_str,
                                   new_database:bool = True,
                                   over_write = False ):
        
        path = self.folder_manager.get_file_path(folder=EnvFolders.OCR_DATABASE_SQLITE, file_name=db_name)
        total_task = 9
        if new_database:
            total_task + 1
            
        with Progress() as progress:
            task_id:TaskID = progress.add_task(f"[cyan]{option_str}", total=total_task)
            
            self.stop_event.clear()
            # START RABBIT 
            self.start_server()
            time.sleep(.5)

            # LOAD VAR IN DATA PROCESSOR
            self.__load_vars_structure_data(dict_tx_options=dict_tx_options)
            progress.update(task_id, advance=1)
            
            # 0: GET MESSAGES FROM RABBIT QUEUE
            list_data_processor = self.__get_queue_data_processor()
            progress.update(task_id, advance=1)

            # 1: GET DATA TO PROCESS
            list_data_queue = self.__load_data_source(list_data_processor=list_data_processor)
            progress.update(task_id, advance=1)

            # 2: LOAD IN QUEUE AGAIN
            self.__republish_data_processor(original_list_processor=list_data_queue)
            progress.update(task_id, advance=1)

            #SET DATA TO CLASS DATA STRUCTURE
            self.__load_data_to_process(list_data_queue)
            progress.update(task_id, advance=1)

            
            
            if new_database :
                self.__create_structure_database(path=path)
                progress.update(task_id, advance=1)
                
                self.__export_data_to_new_database(path=path, progress=progress, task_id= task_id)
            elif not new_database:
                #self.folder_manager.set_foxy_ownership(path=path)
                self.__export_data_to_database(path=path, progress=progress, task_id= task_id, over_write =over_write)
                
            self.folder_manager.change_permissions(path=path)
            progress.update(task_id, advance=1)
            
    def start_data_export_spreadsheet(self, xlsx_nane, dict_tx_options:dict[str,list[str]],option_str):
        path = self.folder_manager.get_file_path(folder=EnvFolders.OCR_SPREADSHEET, file_name=xlsx_nane)

        total_task = 10
        has_links = True
        adjust_columns = True
            
        if adjust_columns:
            total_task += 1

            
        with Progress() as progress:
            task_id = progress.add_task(f"[cyan]{option_str}", total=total_task)
            
            self.stop_event.clear()
            # START RABBIT 
            self.start_server()
            time.sleep(.5)
            # LOAD VAR IN DATA PROCESSOR
            
            self.__load_vars_structure_data(dict_tx_options=dict_tx_options, use_link_image_source_as_key_t2=True)
            progress.update(task_id, advance=1)
            
            # 0: GET MESSAGES FROM RABBIT QUEUE
            list_data_processor = self.__get_queue_data_processor()
            progress.update(task_id, advance=1)

            # 1: GET DATA TO PROCESS
            list_data_queue = self.__load_data_source(list_data_processor=list_data_processor)
            progress.update(task_id, advance=1)

            # 2: LOAD IN QUEUE AGAIN
            self.__republish_data_processor(original_list_processor=list_data_queue)
            progress.update(task_id, advance=1)

            #SET DATA TO CLASS DATA STRUCTURE
            self.__load_data_to_process(list_data_queue)
            progress.update(task_id, advance=1)
            
            self.export_spreadshet(path=path,
                                   progress=progress,
                                   task_id=task_id,
                                   has_links=has_links,
                                   adjust_columns=adjust_columns)
            

 
            self.folder_manager.change_permissions(path=path)
            progress.update(task_id, advance=1)

        
    @ct_log.count_ms
    def __create_structure_database(self, path:str):
        self.create_table_t1_db(path_db=path)
        self.create_table_t2_db(path_db=path)
        self.create_table_tx_db(path=path)
    
    
    @ct_log.count_ms
    def __export_data_to_new_database(self, path, progress:Progress, task_id:TaskID):
        self.load_data_t1_db(path=path)
        progress.update(task_id=task_id, advance=1)
        
        self.load_data_t2_db(path=path)
        progress.update(task_id=task_id, advance=1)

        self.load_data_tx_db(path=path)
        progress.update(task_id=task_id, advance=1)

        
    @ct_log.count_ms
    def __export_data_to_database(self, path, progress:Progress, task_id:TaskID, over_write):
        self.load_data_t1_db(path=path, unique_cols=[self._0_t1_primary_key], overwrite=over_write)
        progress.update(task_id=task_id, advance=1)

        self.load_data_t2_db(path=path,unique_cols=[self.key_image_screenshot_name], overwrite= over_write)
        progress.update(task_id=task_id, advance=1)

        self.load_data_tx_db(path=path, overwrite= over_write)
        progress.update(task_id=task_id, advance=1)


    @ct_log.count_ms
    def __load_vars_structure_data(self, dict_tx_options:dict[str,list], use_link_image_source_as_key_t2 = False):

        keys_to_unpack_in_tx:list[str] = dict_tx_options[SharedKeys.KEYS_TO_UNPACK_IN_TX.value]
        tx_third_index_dimension:list[str] = dict_tx_options[SharedKeys.TX_THIRD_INDEX_DIMENSION.value]
        
        t1_extructure = {
        
        self._0_t1_primary_key: StructureType.STRING.value,
        self._1_t1_key_name: StructureType.STRING.value,
        self._2_t1_key_source: StructureType.STRING.value,
        self._3_t1_key_source_type: StructureType.STRING.value,
        self._4_t1_key_resolution: StructureType.STRING.value}
        
        list_areas_project: list[AreaOcrModel]= self.setting_manager.get_areas_model_from_file_setting()
        list_areas_model_project = [area.get_dict_model_tx() for area in list_areas_project]
        
        
        if use_link_image_source_as_key_t2:
            primary_key_t2 = self.key_image_screenshot_link
        else:
            primary_key_t2 = self.key_image_screenshot_name

            
        t2_tx_structure = {
            self.key_screen_id: StructureType.STRING.value,
            self.key_image_screenshot_name: StructureType.STRING.value,
            self.key_image_screenshot_link: StructureType.STRING.value,
            self.key_collector_data: {
                self.key_session_id: StructureType.STRING.value,
                self.key_session_code: StructureType.STRING.value,
                self.key_is_start_session: StructureType.BOOLEAN.value,
                self.key_is_end_session: StructureType.BOOLEAN.value,
                self.key_is_change_detected: StructureType.BOOLEAN.value,
                self.key_timestamp_seconds: StructureType.DECIMAL.value,
                self.key_session_captures_number: StructureType.INTEGER.value,
                self.key_date: StructureType.STRING.value},
             self.key_areas_ocr: list_areas_model_project }
        
        data_structure_var = DataStructureVar(
            DICT_DATA_EXTRUCTURE_T1 = t1_extructure,
            DICT_DATA_EXTRUCTURE_T2_TX = t2_tx_structure,
            T1_NAME = self.T1_NAME,
            PRIMARY_KEY_T1 = self.key_screen_id,
            TYPE_PRIMARY_KEY_T1 = SqlType.TEXT,
            T2_NAME = self.T2_NAME,
            PRIMARY_KEY_T2 = primary_key_t2,
            TYPE_PRIMARY_KEY_T2 = SqlType.TEXT,
            TX_DEFAULT_NAME = self.project_name,
            KEY_LIST_TABLE_TX = self.key_areas_ocr,
            KEYS_TO_UNPACK_IN_TX = UnpackKeysToTX(KEYS = keys_to_unpack_in_tx) ,
            TX_THIRD_INDEX_DIMENSION = TxThirdIndexDimension(LIST_INDEX = [*tx_third_index_dimension, self.key_area_value]),
            KEYS_TO_AVOID_UNPACK_IN_TX = AvoidUnpackKeysToTX(KEYS=[self.key_areas_ocr]) ,
            TX_DUAL_INDEX = TxDualIndex(INDEX_0 = self.key_area_group, 
                                        INDEX_1 = self.key_area_name),
            KEYS_TO_UNPACK_IN_DATA_DICT_T2 =  UnpackKeysToT2(KEYS = [self.key_collector_data]) ,
            KEYS_TO_AVOID_UNPACK_DATA_DICT_T2 = AvoidUnpackKeysToT2(KEYS = [self.key_areas_ocr]),
            SHARED_FOREIGN_KEY_T1_T2 = self.key_screen_id,
            SHARED_FOREIGN_KEY_T2_TX =  primary_key_t2,
            IS_SHARED_FOREIGN_KEY_IN_T2_PRIMARY_KEY = False,
            IS_SHARED_FOREIGN_KEY_IN_TX_PRIMARY_KEY = True)
        
        
        self.init_variables_structure(data_structure_var=data_structure_var)
        
    def __load_data_to_process(self, list_data_t2_tx):
            
        data_t1 = {
        self._0_t1_primary_key: self.screen_id,
        self._1_t1_key_name: self.project_name,
        self._2_t1_key_source: self.setting_manager.project_source,
        self._3_t1_key_source_type:self.setting_manager.project_source_type.value,
        self._4_t1_key_resolution:self.setting_manager.project_resolution.string_value,}
        self.init_variables_data(dict_data_source_t1=data_t1, lis_data_source_t2_tx=list_data_t2_tx)
        
        
    
    @ct_log.count_ms
    @ct_log.count_kb
    def __get_queue_data_processor(self) -> list[bytes]:
        return  self.get_queue_message()
    
    @ct_log.count_ms
    def __load_data_source(self, list_data_processor:list[bytes])-> list[dict[str, any]]:
        list_data_queue = []
        try:
            for body in list_data_processor:
                data = body.decode()
                data_json = json.loads(data)
                data_dict = data_json['data']
                #print(data_dict)
                list_data_queue.append(data_dict)
        except Exception as e:
            print(f"Error decoding data json load.: {e}")
            raise e

        return list_data_queue 
    def stop_process(self):
        self.__set_current_data_task_dict(message= "Data Export to Database Stopped by User")


    def __init_rabbit_processor_handler(self):
        queue_name:str = RabbitMqEnv.get_queue_name(filter_module_source=PROCESSOR_MODULE_SOURCE, screen_id=self.screen_id)
        routing_key:str = RabbitMqEnv.get_routing_key_name(filter_module_source=PROCESSOR_MODULE_SOURCE, screen_id=self.screen_id)
      
        instance:RabbitMQ = RabbitMQ(  host=Env.RABBITMQ_HOST.value,
                                        username=Env.RABBITMQ_USERNAME.value,
                                        password=Env.RABBITMQ_PASSSWORD.value,
                                        exchange=Env.RABBITMQ_EXCHANGE.value,
                                        routing_key=routing_key,
                                        queue_name=queue_name)
        
        
        self._rabbit_processor:Handler  = Handler(instance)
        self._rabbit_processor.rabbitmq.start_server()


    def __set_current_data_task_dict(self, 
                                   message:str = None,
                                   error_message:str = None) -> None:
        
        self._error_message = error_message
        self._message = message
       
    @ct_log.count_ms
    def __republish_data_processor(self, original_list_processor:list[dict[str,any]]):
        for data in original_list_processor:
            self.rabbit_processor.publish_data(data)
        self.__close_rabbit_processor_handler()
        
    def __close_rabbit_processor_handler(self):
        if self._rabbit_processor is not None:
            self._rabbit_processor.rabbitmq.close_active_connection()
            self._rabbit_processor = None


        

    # def export_db_with_inquirer(self, database_name: str, export_path: str):
    #     columns = self.get_columns_from_db(database_name)
    #     ignore_columns = self.prompt_ignore_columns(columns)
    #     self.export_db_to_xlsx(database_name, export_path, ignore_columns)

    


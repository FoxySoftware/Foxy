import json
import threading
import time
from types import NoneType
import cv2
import datetime
import numpy as np
from api.gateway.rabbitmq_env import  PROCESSOR_MODULE_SOURCE, RabbitMqEnv
from folder_manager import FolderManager
from ocr_processor import OcrProcessor
from base_class.shared_keys import SharedKeys
from screenshot_model import CaptureSession, ImageModel, ScreenShotModel
from processor.base_class.os_env_geral import OsEnvGeneral as Env

from api.gateway.rabbitmq import RabbitMQ
from api.services.handler import Handler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from settings_manager import SettingManager


class ImageProcessor(RabbitMQ):

    def __init__(self, **kwargs):
        super().__init__( **kwargs)
        self._id_instance_collector_consume = kwargs["id_instance_collector_consume"]
        self.stop_event:threading.Event = kwargs.get("stop_event",  threading.Event())
        self.pause_event:threading.Event = kwargs.get("pause_event",  threading.Event())                
        self.session_id:str = kwargs["session_id"] # screen_id
        self._folder_manager = kwargs["folder_manager"]
        self._ocr_processor:callable = kwargs["ocr_processor"]
        self._setting_manager:callable = kwargs["setting_manager"]
        self._rabbit_processor:Handler | None = None
        self._total_processed:int = 0
        self._total_in_queue_collector: int | None = None
        self._current_image_name:str | None  = None
        self._current_areas_processed : dict[str, any] | None = None
        self._message:str | None = None
        self._error_message:str | None  = None

    @property
    def ocr_processor(self)-> OcrProcessor:
        return self._ocr_processor()

    @property
    def folder_manager(self)-> FolderManager:
        return self._folder_manager()

    @property
    def setting_manager(self) -> 'SettingManager': 
        return self._setting_manager()
    
    @property
    def rabbit_processor(self) -> Handler: 
        if  self._rabbit_processor is None :
            self.__init_rabbit_processor_handler()
        return self._rabbit_processor
    
    def get_current_task_properties(self) -> dict[str, str] | None:
        data_dict = None
   
        if isinstance(self._current_areas_processed, dict):
            self._check_message_in_queue_collector()
            if self._total_in_queue_collector is None:
                _total_in_queue_collector_str = "--"
            else:
                _total_in_queue_collector_str = str(self._total_in_queue_collector)
                
            str_dict = {key: str(value) for key, value in self._current_areas_processed.items()}
            data_dict = { "total_processed": str(self._total_processed),
                          "total_in_queue_to_process": _total_in_queue_collector_str,
                          "current_screenshot":self._current_image_name,
                          **str_dict
                         }
        
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
    
    def start_consume_collector(self):
        self.set_current_data_task_dict(screenshot=None, message= "Image OCR Processor Started")
        self.stop_event.clear()
        self.pause_event.clear()
        self.start_server()
        #just in case. sleep .5
        time.sleep(0.5)
        count = self._check_message_in_queue_collector()
        if count == 0:
            self.set_current_data_task_dict(screenshot=None, message= "Empty Queue. Awaiting for incoming Image to process")
        self.consume_queue(consumer_tag=self._id_instance_collector_consume)
    
    def _check_message_in_queue_collector(self) -> int | None:
        count = None
        try:
            count = self._active_queue.method.message_count
        except:
            pass
        self._total_in_queue_collector = count
        return count
                
    def stop_consume_collector(self, channel= None):
        self.set_current_data_task_dict(screenshot=None, message= "Image OCR Processor Stopped by User")
        if channel is not None:
            channel.basic_cancel(self._id_instance_collector_consume)
            channel.stop_consuming(self._id_instance_collector_consume)
            self.close_active_connection()
        else:
            self.safe_close_active_queue(self._id_instance_collector_consume)
            self.close_active_connection()
            self.__close_rabbit_processor_handler()

    def _pause_consume_collector(self, channel):
        self.set_current_data_task_dict(screenshot=None, message= "Image OCR Processor Paused")
        channel.basic_cancel(self._id_instance_collector_consume)

    def reassume_consume_collector(self):
        self.stop_event.clear()
        self.pause_event.clear()
        self.consume_queue(consumer_tag=self._id_instance_collector_consume)
    
    
    def callback(self, channel, method, properties, body:bytes):
        if self.stop_event.is_set() :
            self.stop_consume_collector(channel=channel)
            return
        if self.pause_event.is_set():
            self._pause_consume_collector(channel=channel)
            return
        
        data = body.decode()
        data_json = json.loads(data)
        self.current_object_from_queue =  data_json['data']
        try:
            screenshot_model= self.ocr_screenshot_builder(data_json)
        except ImageNoFoundError as e:
            self.set_current_data_task_dict(screenshot=None, error_message=f"ImageNoFoundError: {e}")
            channel.basic_ack(delivery_tag=method.delivery_tag)
        
        screenshot_model_processed = self.ocr_processor.main_ocr_process(screenshot_model=screenshot_model)
        self.set_current_data_task_dict(screenshot=screenshot_model_processed)
        dict_screenshot_model = screenshot_model_processed.to_final_dict()
        self.__publish_screenshot(data_dict=dict_screenshot_model)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    

    def __init_rabbit_processor_handler(self):
        queue_name:str = RabbitMqEnv.get_queue_name(filter_module_source=PROCESSOR_MODULE_SOURCE, screen_id=self.session_id)
        routing_key:str = RabbitMqEnv.get_routing_key_name(filter_module_source=PROCESSOR_MODULE_SOURCE, screen_id=self.session_id)
      
        instance:RabbitMQ = RabbitMQ(  host=Env.RABBITMQ_HOST.value,
                                        username=Env.RABBITMQ_USERNAME.value,
                                        password=Env.RABBITMQ_PASSSWORD.value,
                                        exchange=Env.RABBITMQ_EXCHANGE.value,
                                        routing_key=routing_key,
                                        queue_name=queue_name)
        
        
        self._rabbit_processor:Handler  = Handler(instance)
        self._rabbit_processor.rabbitmq.start_server()

    def __close_rabbit_processor_handler(self):
        if self._rabbit_processor is not None:
            self._rabbit_processor.rabbitmq.close_active_connection()
            self._rabbit_processor = None

    def set_current_data_task_dict(self, screenshot:ScreenShotModel | None, 
                                   message:str = None,
                                   error_message:str = None) -> None:
        if isinstance(screenshot, ScreenShotModel):
            self._current_areas_processed = screenshot.get_basic_dict_areas()
            
            self._current_image_name = screenshot.image_source_model.name
        self._error_message = error_message
        self._message = message
       
    
    def __publish_screenshot(self, data_dict:dict):
        self.rabbit_processor.publish_data(data_dict)
        self._total_processed += 1
        
    def ocr_screenshot_builder(self,data_from_queue:dict[str, any]) -> ScreenShotModel :
        data = data_from_queue["data"]
        image_full_path = data["path_image"]
        image_name:str = self.folder_manager.get_file_name_from_path(path=image_full_path)
        image_path:str = image_full_path
        try:
            image:np.ndarray = cv2.imread(image_full_path)
        except Exception:
            raise ImageNoFoundError(message=f"{image_full_path} not found ")
        
        list_areas_model = self.setting_manager.get_areas_model_from_file_setting()
        
        image_source = ImageModel(
           name=image_name,
           image=image,
           path=image_path)
        
        unix_timestamp:int =  int(data["unix_timestamp"])
        dt = datetime.datetime.fromtimestamp(unix_timestamp)
        formatted_time = dt.strftime('%a %b %d %Y %H:%M:%S GMT%z')

        capture_session = CaptureSession(
            session_id=data["session_id"],
            session_code= data["session_code"],
            is_start_session=data["is_start_session_trigger"],
            is_end_session=data["is_end_session_trigger"],
            is_change_detected=data["is_change_detected"],
            timestamp_seconds=data["timer_start_session"],
            date= formatted_time,
            session_captures_number=data["counter_screenshot_per_session"])
        
        screenshot_model = ScreenShotModel(
            folder_manager=self.folder_manager,
            screen_id=data["screen_id"],
            test_mode=False,
            save_image_cropped=True,
            image_source_model=image_source,
            list_area_model=list_areas_model,
            capture_session=capture_session
        )

        return screenshot_model
        
        
    
class ImageNoFoundError(Exception):
    """Base class for custom exceptions."""
    def __init__(self, message= "Image no found", code=100):
        super().__init__(message)  
        self.code = code          

    def __str__(self):
        # Provide a custom string representation
        return f"{self.args[0]} (Error code: {self.code})"


from typing import List
import cv2
import numpy as np
from cv2.typing import MatLike
from config_manager import ConfigManager
from base_class.area import Area, ComparisonArea, TriggerArea
from base_class.config_sections import ConfigSections as ConfSec
from base_class.resolution_dataclass import Resolution
from base_class.source_mode import SourceMode
from base_class.triggers import EndSessionTriggerImage, StartSessionTriggerImage, TriggerImage
from folder_manager import FolderManager, EnvFolders
from base_class.os_env_geral import OsEnvGeneral as Env

from PIL import Image


FILE_HSV_RESOURCE_PATH:str = "collector/resource_collector/area_color.png"

class ImageManager():
    
    def __init__(self, folder_manager:FolderManager,
                 screen_resolution:Resolution,
                 current_mode: SourceMode,
                 **kwargs,
                  ) -> None:
        self.current_mode:SourceMode = current_mode
        self.folder_manager = folder_manager
        path_settings:str=self.folder_manager.get_file_path(folder=EnvFolders.MAIN_FOLDER,
                                                            file_name=Env.NAME_FILE_SETTINGS.value)
        self.config_manager = ConfigManager(path_settings)
        self.config_data = None   
        self.reloaded_data_config = None
        
        self.screen_resolution =  screen_resolution
        self.hsv_lower_color:np.ndarray =  None #np.array([60, 50, 50])  # Lower bound for specified color in HSV
        self.hsv_upper_color:np.ndarray = None #np.array([80, 255, 255])  # Upper bound for specified color in HSV
        self.start_trigger_image: StartSessionTriggerImage = None
        self.end_trigger_image:EndSessionTriggerImage = None
        self.resolution_start_trigger_image:str = ""
        self.resolution_end_trigger_image:str = ""
        self.list_trigger_images_name_resolution = []
        self.minimum_area_trigger_width = 0
        self.minimum_area_trigger_height = 0
        
        self.threshold_similarity_start_percent:float = 90
        self.threshold_similarity_list_percent:float = 90
        self.threshold_similarity_end_percent:float = 90
        self.threshold_difference_comparison_area_percent:float = 5
                
        self.video_required:bool = True
        self.start_trigger_required = True
        self.end_trigger_required = False
        self.others_trigger_required = False
        self.interest_trigger_area_required:bool = True
        self.comparison_area_required:bool = True
        self.hsv_color_area_required:bool = True

        # info variables no used for the software
        self.video_name = ""
        self.video_resolution = ""
        self.video_seconds_recording = ""
        self.video_error_message = ""
        self.video_fps = ""
    
 
        self.name_start_trigger_image = ""
        self.start_trigger_image_error_message:str = "" 
        self.name_end_trigger_image = ""
        self.interest_trigger_area_file_name:str = ""
        self.interest_trigger_area_file_resolution:str = ""
        self.interest_trigger_area_resolution:str = ""
        self.interest_trigger_area_error_message:str = ""
        
        self.comparison_area_file_name:str = ""
        self.comparison_area_resolution:str = ""
        self.comparison_area_file_resolution:str = ""
        self.comparison_area_error_message:str = ""

        self.hsv_file_name:str = ""
        self.hsv_color:str = ""
        self.rgb_color:str = ""
        self.hex_color:str = ""
        self.hsv_color_error_message:str = ""
        self.link_hsv_color:str = ""
        
        self.current_task:str = ""
        self.total_captures_files:str = "" # ok self.capture_session_data
        self.elapse_process_percent:str = "" # ok image collector calculate_fps_process
        self.elapse_process_time:str = "" # ok image collector calculate_fps_process
        self.fps_process:str = "" # ok image_collector calculate_fps_process
        self.total_sub_session:str = "" # ok image_collector __notify_screen_shot
        self.updated_at:str = ""
        
        self.load_and_save_config_data()
        

    
    def capture_session_info(self) -> dict[str, str]:
        self.total_captures_files = str(self.folder_manager.count_files_with_extension(folder=EnvFolders.CAPTURES, extension=".png"))
        self.dict_capture_session =  {ConfSec.CAPTURES.value:{  "session_name": self.screen_id,
                                                                "current_task": self.current_task,
                                                                "total_captures_files":self.total_captures_files,
                                                                "elapse_process_percent_%": self.elapse_process_percent,
                                                                "elapse_process_time":self.elapse_process_time,
                                                                "fps_process":self.fps_process,
                                                                "total_sub_session":self.total_sub_session,
                                                                "updated_at":self.updated_at,
                                                                "folder" : self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.CAPTURES),
                                                                                                          is_path_folder=True)
                                                                    }}

        return self.dict_capture_session[ConfSec.CAPTURES.value]
    
    def clear_variables(self):
        self.current_task:str = ""
        self.total_captures_files:str = "" # ok self.capture_session_data
        self.elapse_process_percent:str = "" # ok image collector calculate_fps_process
        self.elapse_process_time:str = "" # ok image collector calculate_fps_process
        self.fps_process:str = "" # ok image_collector calculate_fps_process
        self.total_sub_session:str = "" # ok image_collector __notify_screen_shot
        self.updated_at:str = ""
        
    def load_default_color_image(self):
        file_hsv_resource_path = FILE_HSV_RESOURCE_PATH
        self.folder_manager.copy_file(file_path=file_hsv_resource_path, folder=EnvFolders.HSV_COLOR_AREA)

    def load_config_in_self_variables(self):
        for section, dict_conf in self.config_data.items():
            if section == ConfSec.START_SESSION_TRIGGER_IMAGE.value: 
                self.threshold_similarity_start_percent = float(dict_conf.get("threshold_similarity_%",self.threshold_similarity_start_percent))
            if section == ConfSec.END_SESSION_TRIGGER_IMAGE.value: 
                self.threshold_similarity_end_percent = float(dict_conf.get("threshold_similarity_%", self.threshold_similarity_end_percent))
            if section == ConfSec.LIST_TRIGGER_IMAGES.value:
                self.threshold_similarity_list_percent = float(dict_conf.get("threshold_similarity_%", self.threshold_similarity_list_percent))
            if section == ConfSec.COMPARISON_AREA.value:
                self.threshold_difference_comparison_area_percent = float(dict_conf.get("threshold_difference_%", self.threshold_difference_comparison_area_percent))
            
            if section == ConfSec.CAPTURES.value:
                session_name:str = dict_conf["session_name"]
                if session_name == self.screen_id :
                    self.current_task:str = dict_conf.get("current_task", "")
                    self.total_captures_files:str = dict_conf.get("total_captures_files", "")
                    self.elapse_process_percent:str = dict_conf.get("elapse_process_percent", "")
                    self.elapse_process_time:str = dict_conf.get("elapse_process_time", "")
                    self.fps_process:str = dict_conf.get("fps_process", "")
                    self.total_sub_session:str = dict_conf.get("total_sub_session", "")
                    self.updated_at:str = dict_conf.get("updated_at", "")
                    

                
    def load_and_save_config_data(self) -> dict[str,str]:
        self.config_data = self.config_manager.load_ini_to_dict()
        self.load_config_in_self_variables()
        self.get_trigger_info()
        self.get_interest_trigger_area_info()
        self.get_area_comparison_info()
        self.get_video_info()
        previous_info_capture_dict = self.capture_session_info()
        if not previous_info_capture_dict["session_name"]:
            previous_info_capture_dict = {}
        else:
            previous_info_capture_dict = self.dict_capture_session
        
        dict_video = { "required": str(self.video_required), 
                        "file_name":self.video_name,
                        "duration_seconds":self.video_seconds_recording,
                        "resolution": self.video_resolution,
                        "fps":self.video_fps,
                        "error_message":self.video_error_message,
                        }
        
        if self.current_mode == SourceMode.WEB:
            dict_video["video"] = self.folder_manager.get_link(path=self.folder_manager.get_the_recent_file_path(folder=EnvFolders.SCREEN_RECORDING,
                                                                                                                 only_extension=".avi"))
            
            dict_video["folder"] = self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.SCREEN_RECORDING),
                                                                                                          is_path_folder=True)
            dict_video:dict[str, str] = {ConfSec.SCREEN_RECORDING.value:dict_video}
        elif self.current_mode == SourceMode.VIDEO:
            dict_video["video"] = self.folder_manager.get_link(path=self.folder_manager.get_the_recent_file_path(folder=EnvFolders.VIDEO_SOURCE,
                                                                                                                 only_extension=".mp4"))

            dict_video["folder"] = self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.VIDEO_SOURCE,),
                                                                                                          is_path_folder=True)
            dict_video:dict[str, str] = {ConfSec.VIDEO_SOURCE.value:dict_video}
            
        
        self.reloaded_data_config = {**dict_video, 
                                   
                                   ConfSec.START_SESSION_TRIGGER_IMAGE.value: {"required":str(self.start_trigger_required), 
                                                                    "file_name":self.name_start_trigger_image,
                                                                    "resolution":self.resolution_start_trigger_image, 
                                                                    "threshold_similarity_%":self.threshold_similarity_start_percent,
                                                                    "error_message":self.start_trigger_image_error_message,
                                                                    "image":self.folder_manager.get_link(path=self.folder_manager.get_the_recent_file_path(folder=EnvFolders.START_SESSION_TRIGGER_IMAGE, only_extension=".png")),
                                                                    "folder" : self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.START_SESSION_TRIGGER_IMAGE,),
                                                                                                          is_path_folder=True)
                                                                    },
                                   
                                    ConfSec.END_SESSION_TRIGGER_IMAGE.value: {"required":str(self.end_trigger_required), 
                                                                  "file_name":self.name_end_trigger_image,
                                                                  "resolution":self.resolution_end_trigger_image,
                                                                  "threshold_similarity_%":self.threshold_similarity_end_percent,
                                                                  "image":self.folder_manager.get_link(path=self.folder_manager.get_the_recent_file_path(folder=EnvFolders.END_SESSION_TRIGGER_IMAGE, only_extension=".png")),
                                                                  "folder" : self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.END_SESSION_TRIGGER_IMAGE),is_path_folder=True)
                                                                  },
                                    
                                    ConfSec.LIST_TRIGGER_IMAGES.value:{"required":str(self.others_trigger_required), 
                                                                        "list_triggers":self.list_trigger_images_name_resolution,
                                                                        "threshold_similarity_%":self.threshold_similarity_list_percent,
                                                                        "folder" : self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.LIST_TRIGGER_IMAGES),is_path_folder=True)
                                                                        },
                                    
                                    ConfSec.INTEREST_TRIGGER_AREA.value:{'required':str(self.interest_trigger_area_required), 
                                                                        "file_name":self.interest_trigger_area_file_name,
                                                                        "resolution_file":self.interest_trigger_area_file_resolution,
                                                                        "resolution_area":self.interest_trigger_area_resolution,
                                                                        "minimum_resolution_area": f"{self.minimum_area_trigger_width}, {self.minimum_area_trigger_height}",
                                                                        "error_message":self.interest_trigger_area_error_message,
                                                                        "image":self.folder_manager.get_link(path=self.folder_manager.get_the_recent_file_path(folder=EnvFolders.INTEREST_TRIGGER_AREA, only_extension=".png")),
                                                                        "folder" : self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.INTEREST_TRIGGER_AREA),is_path_folder=True)
                                                                        },
                                                
                                    ConfSec.COMPARISON_AREA.value:{'required':str(self.comparison_area_required),
                                                       "file_name":self.comparison_area_file_name,
                                                       "resolution_file":self.comparison_area_file_resolution,
                                                       "resolution_area":self.comparison_area_resolution,
                                                       "error_message":self.comparison_area_error_message,
                                                       "threshold_difference_%":self.threshold_difference_comparison_area_percent,
                                                       "image":self.folder_manager.get_link(path=self.folder_manager.get_the_recent_file_path(folder=EnvFolders.COMPARISON_AREA, only_extension=".png")),
                                                       "folder" : self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.COMPARISON_AREA),is_path_folder=True)
                                                       },
                                    
                                    **self.get_hsv_color_area_info() ,
                                    
                                    **previous_info_capture_dict,
                                    }

        self.config_data.update(self.reloaded_data_config)
        self.config_manager.save_dict_to_ini(self.config_data)  
        return self.config_data
    
    def get_trigger_info(self):
        list_triggers:list[TriggerImage] = self.create_list_of_trigger_images()
        self.list_trigger_images_name_resolution.clear()
        
        for trigger in list_triggers:
            if isinstance(trigger, StartSessionTriggerImage):
                self.name_start_trigger_image = trigger.name
                self.resolution_start_trigger_image = str(trigger.get_size)
                self.start_trigger_required = False
                continue
            if isinstance(trigger, EndSessionTriggerImage):
                self.name_end_trigger_image = trigger.name
                self.resolution_end_trigger_image = str(trigger.get_size)
                self.end_trigger_required = False
                continue
            self.list_trigger_images_name_resolution.append(f"{trigger.name}: {str(trigger.get_size)}") 
            self.others_trigger_required = False
    
    def get_video_info(self):
        if self.current_mode == SourceMode.WEB:
            video_folder:EnvFolders = EnvFolders.SCREEN_RECORDING
            file_video_path = self.folder_manager.get_the_recent_file_path(folder=video_folder, only_extension=".avi")
        elif self.current_mode == SourceMode.VIDEO:
            video_folder:EnvFolders = EnvFolders.VIDEO_SOURCE 
            file_video_path = self.folder_manager.get_the_recent_file_path(folder=video_folder, only_extension=".mp4")
        if not file_video_path: 
            self.video_error_message = "Video file no found"
            return
        self.video_name = self.folder_manager.get_file_name_from_path(path=file_video_path, without_extension=False)
        video = cv2.VideoCapture(file_video_path)
        self.video_fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count and frame_count > 0:
            duration = frame_count / self.video_fps
            self.video_seconds_recording = f"{duration:.2f}"
            self.video_required = False
         # Obtener resolución del video
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.video_resolution = f"({width}x{height})"
    
    @staticmethod
    def get_resolution_video_source(folder_manager:FolderManager)->Resolution:
        video_folder:EnvFolders = EnvFolders.VIDEO_SOURCE 
        file_video_path = folder_manager.get_the_recent_file_path(folder=video_folder, only_extension=".mp4")
        video = cv2.VideoCapture(file_video_path)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return Resolution.from_string(value=f"{width} x {height}")
    
    def get_interest_trigger_area_info(self):
        try:
            self.get_indicators_trigger_area()
        except Exception as e:
            pass
        
    def get_area_comparison_info(self):
        try:
            self.get_area_of_comparison()
        except Exception as e:
            pass
        
    def get_minimum_area_triggers(self):
        list_triggers:list[TriggerImage] = self.create_list_of_trigger_images()
        for trigger in list_triggers:
            width, height = trigger.get_size
            if width > self.minimum_area_trigger_width:
                self.minimum_area_trigger_width = width
            if height > self.minimum_area_trigger_height:
                self.minimum_area_trigger_height = height
        
    def get_area(self, file_mask_path:str, minimum_width, minimum_height, area_type:str = None) -> Area|ValueError:
        
        image = cv2.imread(file_mask_path)
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, self.hsv_lower_color, self.hsv_upper_color)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            if len(approx) == 4:  
                x, y, w, h = cv2.boundingRect(approx)
                if area_type == EnvFolders.INTEREST_TRIGGER_AREA.value :
                    self.interest_trigger_area_resolution = f"{w}, {h}"
                elif area_type == EnvFolders.COMPARISON_AREA.value: 
                    self.comparison_area_resolution = f"{w}, {h}"
                
                if w >= minimum_width and h >= minimum_height:
                    return  Area(x=x, y=y, w=w, h=h)
                else :
                    if area_type == EnvFolders.INTEREST_TRIGGER_AREA.value:
                        self.interest_trigger_area_error_message = "The area found is less than the required area."
                    if area_type == EnvFolders.COMPARISON_AREA.value:
                        self.comparison_area_error_message = "The area found is less than the required area."
                    raise ValueError("The area found is less than the required area.")
                
        if area_type == EnvFolders.INTEREST_TRIGGER_AREA.value:
            self.interest_trigger_area_error_message = "Area no founded in the image"
        if area_type == EnvFolders.COMPARISON_AREA.value:
            self.comparison_area_error_message = "Area no founded in the image"    
        raise ValueError("Area no founded in the image")

    def get_indicators_trigger_area(self) -> TriggerArea|ValueError:
        #MARK: Get area of interest
        self.get_minimum_area_triggers()
        area_image_folder = EnvFolders.INTEREST_TRIGGER_AREA
        file_mask_path = self.folder_manager.get_the_recent_file_path(folder=area_image_folder, only_extension=".png")
        if not file_mask_path: 
            self.interest_trigger_area_error_message = "Image file no found"
            raise ValueError(self.interest_trigger_area_error_message)
        width_image = 0
        height_image = 0
        with Image.open(file_mask_path) as img:
            width_image = img.width
            height_image = img.height
            self.interest_trigger_area_file_resolution = str(img.size)
        error_message:str = f"Resolution image is not {self.screen_resolution.string_value}"
        
        if self.screen_resolution.value[0] !=  width_image:
            self.interest_trigger_area_error_message = error_message
            raise ValueError(error_message)
        if self.screen_resolution.value[1] !=  height_image:
            self.interest_trigger_area_error_message = error_message
            raise ValueError(error_message)
        self.interest_trigger_area_file_name = self.folder_manager.get_file_name_from_path(file_mask_path)
        self.get_hsv_color_area_info()
        area = self.get_area(file_mask_path, self.minimum_area_trigger_width, self.minimum_area_trigger_height, EnvFolders.INTEREST_TRIGGER_AREA.value)
        self.interest_trigger_area_required = False
        return area
        
    def get_area_of_comparison(self, minimum_width = 1, minimum_height= 1) -> ComparisonArea|Exception:
        #MARK: Get area of comparison
        area_image_folder = EnvFolders.COMPARISON_AREA
        file_mask_path = self.folder_manager.get_the_recent_file_path(folder=area_image_folder, only_extension=".png")
        if not file_mask_path: 
            self.comparison_area_error_message = "Image file no found"
            raise ValueError("Image file no found")
        width_image = 0
        height_image = 0
        with Image.open(file_mask_path) as img:
            width_image = img.width
            height_image = img.height
            self.comparison_area_file_resolution = str(img.size) 
        error_message:str = f"Resolution image is not {self.screen_resolution.string_value}"
        if self.screen_resolution.value[0] !=  width_image:
            self.comparison_area_error_message = error_message
            raise ValueError(error_message)
        if self.screen_resolution.value[1] !=  height_image:
            self.comparison_area_error_message = error_message
            raise ValueError(error_message)
        self.get_hsv_color_area_info()
        area = self.get_area(file_mask_path, minimum_width, minimum_height,  EnvFolders.COMPARISON_AREA.value)
        self.comparison_area_required = False
        return area
       

    def create_list_of_trigger_images(self) -> List[TriggerImage]:
        #MARK: Create list of triggers images
        list_of_trigger_srt:List[str] = self.get_list_path_trigger()
        list_of_trigger:List[TriggerImage] = []
        for file_path_trigger in list_of_trigger_srt:
               
            list_of_trigger.append(TriggerImage(
                name=self.folder_manager.get_file_name_from_path(file_path_trigger),
                path_image=file_path_trigger,
                threshold_trigger_image=self.threshold_similarity_list_percent))
        
        self.start_trigger_image: StartSessionTriggerImage = self.get_last_trigger_start_session()
        self.end_trigger_image:EndSessionTriggerImage = self.get_last_trigger_end_session()
       
        if self.start_trigger_image:
            list_of_trigger.append(self.start_trigger_image)
            
        if self.end_trigger_image:
            list_of_trigger.append(self.end_trigger_image)
        
        return list_of_trigger
    
    def get_list_path_trigger(self)-> List[str]:
        list_path_trigger = self.folder_manager.get_list_path_files(folder=EnvFolders.LIST_TRIGGER_IMAGES, extension=".png")
        return list_path_trigger
    
    def get_last_trigger_start_session(self)-> StartSessionTriggerImage | None:
        #MARK: Get last trigger start session
        file_path = self.folder_manager.get_the_recent_file_path(EnvFolders.START_SESSION_TRIGGER_IMAGE, only_extension=".png")
        if not file_path:
            self.start_trigger_image_error_message = "Image file no found"
            return None
        trigger = StartSessionTriggerImage( 
            name=self.folder_manager.get_file_name_from_path(file_path),
            path_image = file_path,
            threshold_trigger_image = self.threshold_similarity_start_percent)
        return trigger
    
    def get_last_trigger_end_session(self)-> EndSessionTriggerImage | None:
        #MARK: Get last trigger end session
        file_path = self.folder_manager.get_the_recent_file_path(EnvFolders.END_SESSION_TRIGGER_IMAGE, only_extension=".png")
        if not file_path:
            return None
        
        trigger = EndSessionTriggerImage( 
            name=self.folder_manager.get_file_name_from_path(file_path),
            path_image = file_path,
            threshold_trigger_image = self.threshold_similarity_end_percent)
        return trigger
    
    def draw_trigger_rectangle(self, image:MatLike, x:int, y:int, w:int, h:int, loc:np.ndarray):
        #MARK: Draw rectangle rectangle
        for pt in zip(*loc[::-1]):
            pt = (pt[0] + x, pt[1] + y)
            cv2.rectangle(image, pt,
                        (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        return image
    
            # create new image from thi result
    def draw_rectangle(self, image:MatLike, x:int, y:int, w:int, h:int):
        #MARK: Draw rectangle
        # add offset to x and y and w and h to create a rectangle more bigger
        x = x - 20
        y = y - 20
        w = w + 40
        h = h + 40
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return image
    
    def get_thresh_diff_images(self, image1, image2, threshold: int = 30, max_value: int = 255) -> MatLike:
        if image1 is None or image2 is None:
            raise ValueError("Input images cannot be None")
        if image1.shape != image2.shape:
            raise ValueError("Input images must have the same dimensions")
        diff = cv2.absdiff(image1, image2)

        if diff.ndim == 2:  # Single-channel image
            gray_diff = diff
        elif diff.ndim == 3 and diff.shape[2] == 3:  # BGR image
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Unexpected image format")

        _, thresh = cv2.threshold(gray_diff, threshold, max_value, cv2.THRESH_BINARY)

        return thresh
        

    
    def get_hsv_color_area_info(self) -> dict[str,dict[str, str]]:
        required = True
        error_message = ""
        file_name = ""
        
        def load_default_color_image():
            self.folder_manager.copy_file(file_path=FILE_HSV_RESOURCE_PATH, folder=EnvFolders.HSV_COLOR_AREA)
        
        file_path = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.HSV_COLOR_AREA, only_extension=".png")
        if not file_path:  
            load_default_color_image()
        file_path = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.HSV_COLOR_AREA, only_extension=".png")
        if not file_path:
            error_message = "Image file no found"
        else:
            try:
                file_name = self.folder_manager.get_file_name_from_path(path=file_path, without_extension=False)
                dict_image_color = self.get_color_info_from_image(image_path=file_path)
                self.hsv_lower_color = dict_image_color["hsv_lower_color"]
                self.hsv_upper_color = dict_image_color["hsv_upper_color"]
                required = False
            except Exception as e:
                error_message = str(e)
        folder_link = ""
        if file_path:
            folder_link = self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.HSV_COLOR_AREA),is_path_folder=True)
            image_link = self.folder_manager.get_link(path=self.folder_manager.get_the_recent_file_path(folder=EnvFolders.HSV_COLOR_AREA, only_extension=".png"))
        return { ConfSec.HSV_COLOR_AREA.value : {
                                    "required" : str(required),
                                    "file_name" :file_name,
                                    "hsv_color" : dict_image_color["hsv_color_str"],
                                    "rgb_color" : dict_image_color["rgb_color_str"],
                                    "hex_color" : dict_image_color["hex_color_str"],
                                    "error_message" :error_message,
                                    "image":image_link,
                                    "folder": folder_link
                    } }


    @staticmethod
    def get_color_info_from_image(image_path: str) -> dict[str, any]:
        """"
        Return:
          hsv_lower_color:np.ndarray |
          hsv_upper_color:np.ndarray |
          hsv_color_str:str |
          rgb_color_str:str |
          hex_color_str:str |     
        """
        image: np.ndarray = cv2.imread(image_path)
       
        # Convert the image from BGR to HSV
        hsv_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        bgr_color: np.ndarray = image[0, 0]  # Color in BGR format
        hsv_color: np.ndarray = hsv_image[0, 0]  # Color in HSV format
        
        hue, saturation, value = hsv_color
        hue_standard: int = round(hue * 2)  # Convert from 0-179 to 0-360
        saturation_standard: int = round((saturation / 255) * 100)  # Convert from 0-255 to 0-100
        value_standard: int = round((value / 255) * 100)  # Convert from 0-255 to 0-100
        
        hsv_lower_color = hsv_color
        hsv_upper_color = hsv_color        
        hsv_color_str = f"({hue_standard}, {saturation_standard}, {value_standard})"    
        
        rgb_color_bgr: np.ndarray = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2RGB)[0, 0]
        rgb_color_standard: tuple[int, int, int] = tuple(map(int, rgb_color_bgr))  # RGB values en rango 0-255
        rgb_color_hex: str = '#{:02X}{:02X}{:02X}'.format(*rgb_color_standard)  # Hexadecimal format

        rgb_color_str = str(rgb_color_standard)
        hex_color_str = str(rgb_color_hex)
        
        return {"hsv_lower_color":hsv_lower_color,
                "hsv_upper_color":hsv_upper_color,
                "hsv_color_str":hsv_color_str,
                "rgb_color_str":rgb_color_str,
                "hex_color_str":hex_color_str      
                }
    
    def get_image(file_path:str)-> np.ndarray:
        return  cv2.imread(file_path)

    
    @staticmethod
    def get_image_resolution(image: np.ndarray) -> tuple[int, int]:
        height: int
        width: int
        height, width, _ = image.shape
        return width, height
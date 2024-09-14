import ast
import re
from types import NoneType
import numpy as np
from area_ocr_processor import AreasOcr
from config_manager import ConfigManager
from folder_manager import FolderManager, EnvFolders
from image_processor import ImageProcessor
from base_class.area_ocr_model import AreaOcrModel
from base_class.menu_project import ConfigMenuProject
from base_class.resolution_dataclass import Resolution
from base_class.sections import AreaSectionsPrefix, ConfigSections
from processor.base_class.os_env_geral import OsEnvGeneral as Env
from processor.base_class.source_mode import SourceMode
from processor.resource_processor import hash_file


menu_ocr_process = ConfigMenuProject.INIT_OCR_PROCESS.value
menu_data_process = ConfigMenuProject.MENU_DATA_PROCESS.value
FILE_HSV_RESOURCE_PATH:str = "processor/resource_processor/area_color.png"

    
class SettingManager():
    
    def __init__(self, folder_manager:FolderManager, **kwargs) -> None:
        self.section_area_prefix = AreaSectionsPrefix.SECTION_AREA_PREFIX.value
        self.section_project = ConfigSections.PROJECT.value
        self.section_hsv_color_area = ConfigSections.HSV_COLOR_AREA.value
        self.section_area_image_ocr = ConfigSections.AREAS_IMAGE_OCR.value
        self.section_area_image_ocr_listed = ConfigSections.AREAS_IMAGE_OCR_LISTED.value
        self.section_setting_areas = ConfigSections.SECTION_SETTING_AREAS_OCR.value
        self.section_sub_images_to_remove = ConfigSections.SUB_IMAGE_TO_REMOVE.value
        self.section_project_state = ConfigSections.PROJECT_SESSION_STATE.value
        
        self.folder_manager = folder_manager
        self._image_processor:callable = kwargs["image_processor"]
        path_settings:str=self.folder_manager.get_file_path(folder=EnvFolders.MAIN_FOLDER, file_name=Env.NAME_FILE_SETTINGS.value)
        path_setting_areas:str =self.folder_manager.get_file_path(folder=EnvFolders.MAIN_FOLDER, file_name=Env.NAME_FILE_SETTING_AREAS.value)
        self.settings = ConfigManager(path_settings)
        self.setting_areas = ConfigManager(path_setting_areas)
        self.project_name:str = kwargs.get("project_name", None)
        self.screen_id:str = kwargs.get("screen_id", None)
        self.__hsv_lower_color_area:np.ndarray =  None 
        self.__hsv_upper_color_area:np.ndarray = None 
        self.__project_resolution: Resolution = None
        self.__project_section_dict:dict[str,str] = None
        self.__map_areas_state:dict[int,bool] = None
        self.__source:str | None = None
        self.__source_type:SourceMode | None = None
        self.required_areas_orc_image:bool = True
        self.change_area_image_detected:bool = None
        self.check_update_config()
        self.folder_manager.change_permissions(self.folder_manager.get_path(folder=EnvFolders.MAIN_FOLDER))
        self.folder_manager.empty_folder(folder=EnvFolders.TEMP_FILES)
        self._gpu_ocr:bool | None = None
        

    @property
    def image_processor(self) -> ImageProcessor:
        return self._image_processor()
    
    
    def new_image_area_ocr_listed(self) -> None:
        self.create_image_areas_listed()
        dict_data_areas_ocr_listed = self.get_info_image_areas_listed()
        self.settings.update_section(section=self.section_area_image_ocr_listed,
                                     data_dict=dict_data_areas_ocr_listed[self.section_area_image_ocr_listed] )
        return
        
    def get_dict_setting_file(self) -> dict[str,dict[str,str]]:
        return self.settings.load_ini_to_dict()
    
    def get_dict_setting_areas_file(self) -> dict[str,dict[str,str]]:
        return self.setting_areas.load_ini_to_dict()
    
    def update_section_hsv_color(self) -> None:
        section_name = self.section_hsv_color_area
        dict_data = self.get_hsv_color_area_info()
        self.settings.update_section(section=section_name, data_dict=dict_data[section_name])
    
    def update_gpu_ocr(self, gpu_ocr:bool = False) -> None:
        self.settings.update_section(section=self.section_project, data_dict={"gpu_ocr": str(gpu_ocr)})
        
                
    def check_update_config(self) -> None:
        dict_ini_file = self.get_dict_setting_file() 
        if self.project_section_dict[self.section_project]["screen_id"] != self.screen_id:
            self.settings.update_section(section=self.section_project, data_dict={"screen_id":self.screen_id,} )
        
        dict_data_color_areas = self.get_hsv_color_area_info()
        if dict_ini_file.get(self.section_hsv_color_area, None) != dict_data_color_areas:
            self.settings.update_section(section=self.section_hsv_color_area, data_dict=dict_data_color_areas[self.section_hsv_color_area])
        
        dict_data_areas_ocr = self.get_info_image_areas()
        if dict_ini_file.get(self.section_area_image_ocr, None) != dict_data_areas_ocr[self.section_area_image_ocr]:
            self.settings.update_section(section=self.section_area_image_ocr, data_dict=dict_data_areas_ocr[self.section_area_image_ocr])
            self.change_area_image_detected = True
            self.new_image_area_ocr_listed()
            
        dict_data_areas_ocr_listed = self.get_info_image_areas_listed()
        if dict_ini_file.get(self.section_area_image_ocr_listed, None) != dict_data_areas_ocr_listed[self.section_area_image_ocr_listed]:
            self.new_image_area_ocr_listed()
        
        dict_data_setting_area =self.get_info_setting_areas_file()
        if dict_ini_file.get(self.section_setting_areas, None) != dict_data_setting_area[self.section_setting_areas]:
            self.settings.update_section(section=self.section_setting_areas, data_dict= dict_data_setting_area[self.section_setting_areas])
        
        dict_queues_collector_processor = self.get_queues_session_info()
        if dict_ini_file.get(self.section_project_state, None) != dict_queues_collector_processor[self.section_project_state]:
            self.settings.update_section(section=self.section_project_state, data_dict= dict_queues_collector_processor[self.section_project_state])
            
        dict_sub_img_to_remove = self.get_list_sub_image_to_remove_info()
        if dict_ini_file.get(self.section_sub_images_to_remove, None) != dict_sub_img_to_remove[self.section_sub_images_to_remove]:
            self.settings.update_section(section=self.section_sub_images_to_remove, data_dict= dict_sub_img_to_remove[self.section_sub_images_to_remove])

        return
        
        
        
    def get_info_image_areas(self) -> dict[str, dict[str, str]]:
       states:dict[str,bool] = {"True":True, "False":False}
       dict_info = self.__get_image_areas_ocr(folder=EnvFolders.AREAS_IMAGE_OCR, section= self.section_area_image_ocr)
       required_string:str = dict_info[self.section_area_image_ocr]["required"]
       self.required_areas_orc_image = states[required_string]
       return dict_info
            
    def get_info_image_areas_listed(self) -> dict[str, dict[str, str]]:
        return self.__get_image_areas_ocr(folder=EnvFolders.AREAS_IMAGE_OCR_LISTED, section= self.section_area_image_ocr_listed)
        
    @property
    def map_areas_state(self) -> dict[int, bool]:
        if not self.__map_areas_state:
            self.get_info_setting_areas_file()
        return self.__map_areas_state
    
    @property
    def project_resolution(self) -> Resolution:
        if not self.__project_resolution:
            self.load_project_section_from_config()
        return self.__project_resolution
    
    @property
    def project_source_type(self) -> SourceMode:
        if not self.__source_type:
            self.load_project_section_from_config()
        return self.__source_type
    
    @property
    def project_source(self) -> str:
        if not self.__source:
            self.load_project_section_from_config()
        return self.__source
    
    @property
    def gpu_ocr(self) -> bool:
        if not self._gpu_ocr:
            self.load_project_section_from_config()
        return self._gpu_ocr
    
    @property
    def project_section_dict(self):
        if not self.__project_section_dict:
            self.load_project_section_from_config()
        return self.__project_section_dict
    
    @property
    def hsv_lower_area(self) -> np.ndarray:
        if self.__hsv_lower_color_area is None:
            self.get_hsv_color_area_info()
        return self.__hsv_lower_color_area
        
    @property
    def hsv_upper_area(self)-> np.ndarray:
        if self.__hsv_upper_color_area is None:
            self.get_hsv_color_area_info()
        return self.__hsv_upper_color_area
    
    
    def load_project_section_from_config(self) -> dict[str, dict[str, str]]:
        def str_to_bool(value: str) -> bool:
            return value.lower() in ("true", "1", "yes")

        dict_config = self.settings.get_dict_section(section_name=self.section_project)
        self.__project_section_dict = dict_config          

        inner_dict = dict_config[self.section_project]
        resolution:str = inner_dict["screen_resolution"]
        
        self.__project_resolution = Resolution.from_string(resolution)
        self._gpu_ocr = str_to_bool(value=inner_dict.get("gpu_ocr", "False"))
        
        mode_str:str | None = inner_dict.get("mode", None)
        if mode_str:
            mode:SourceMode = SourceMode._from_name(name=mode_str)
            if mode == SourceMode.WEB:
                url = inner_dict.get("url", None)
                if url:
                    pattern = r'\[link=[^\]]+\](http[s]?://[^\[]+)\[/link\]'
                    match = re.search(pattern, url)
                    self.__source:str = match.group(1)
            elif mode == SourceMode.VIDEO:
                    self.__source:str = inner_dict.get("video_name", None)
            self.__source_type = mode
            
        return dict_config

    def get_queues_session_info(self) -> dict[str, str]:
        section_name = self.section_project_state
        session_id = self.screen_id
        error_message: str = ""
        total_captures_files: int | None = None
        total_in_queue_collector: int | None = None
        total_queue_processed: int | None = None
        warning: str = ""
        dependent_list = [menu_ocr_process, menu_data_process]

        try:
            total_in_queue_collector = self.image_processor.count_message_in_queue()
        except Exception as e:
            error_message += f"[red]Error in count queue of image to process[/red]\n"
        try:
            total_queue_processed = self.image_processor.rabbit_processor.rabbitmq.count_message_in_queue()
        except Exception as e:
            error_message += f"[red]Error in count queue of image processed[/red]\n"

        try:
            total_captures_files = self.folder_manager.count_files_with_extension(folder=EnvFolders.CAPTURES, extension=".png")
        except Exception as e:

            error_message += f"[red]Error in counting capture images in folder[/red]\n"

        if total_in_queue_collector is not None and total_captures_files is not None and total_captures_files > 0:
            dependent_list.remove(menu_ocr_process)

        if total_queue_processed is not None and total_queue_processed > 0:
            dependent_list.remove(menu_data_process)

        if total_in_queue_collector is not None \
            and total_captures_files is not None \
            and total_in_queue_collector > total_captures_files:
            warning = f"[red]![/red] Discrepancy with the number of images available and queue."

        session_info = {
            section_name: {
                "session": session_id,
                "queue_to_process": str(total_in_queue_collector) if total_in_queue_collector is not None else "--",
                "queue_processed": str(total_queue_processed) if total_queue_processed is not None else "--",
                "total_screenshot": str(total_captures_files) if total_captures_files is not None else "--",
                "error_message": error_message.strip(),
                "warning_message": warning,
                "_dependent_list": str(dependent_list),
                "folder_captures": self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.CAPTURES),is_path_folder=True, string_link= "Screenshots 🗂️"),
                "folder_db_sqlite": self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.OCR_DATABASE_SQLITE), is_path_folder=True, string_link="SqLite DB 🗂️"), 
                "folder_spreadsheet": self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.OCR_SPREADSHEET), is_path_folder=True, string_link="SpreadSheet 🗂️") 


            }
        }

        return session_info


    
    def __get_image_areas_ocr(self, folder: EnvFolders, section:str) -> dict[str,dict[str,str]]:
        
        required = True
        total_areas = 0
        error_message = ""
        file_name = ""
        width = 0
        height = 0
        section_name = section
        file_path = None
        
        def get_dict():
            link = ""
            if file_path:
                link = self.folder_manager.get_link(path=file_path)
                
            dict_info = { section_name : {
                            "required" : str(required),
                            "total_areas" :  str(total_areas),
                            "file_name": file_name,
                            "resolution_image": f"{width}, {height}",
                            "required_resolution" : self.project_resolution.string_value,
                            "image":link,
                            "folder": self.folder_manager.get_link(path=self.folder_manager.get_path(folder=folder),is_path_folder=True),
                            "hash_file": hash_file.hash_file(file_path=file_path),
                            "error_message" :error_message,
 
                    } }
            if section == self.section_area_image_ocr_listed:
                dict_info[section_name].pop("total_areas")
            return  dict_info
            
        file_path = self.folder_manager.get_the_recent_file_path(folder=folder, only_extension=".png")
        if not file_path:
            error_message = "Image file no found"
            return get_dict()
        file_name = self.folder_manager.get_file_name_from_path(path=file_path, without_extension=False)
        
        list_areas, image =  AreasOcr.identify_green_box( file_mask_path=file_path,
                                                         hsv_lower_color_area=self.hsv_lower_area,
                                                         hsv_upper_color_area= self.hsv_upper_area)
        total_areas = len(list_areas)
        if total_areas == 0 and section == self.section_area_image_ocr:
            error_message = "None area found"
            return get_dict()
        
        width, height = AreasOcr.get_image_resolution(image)
        if width != self.project_resolution.value[0] or height != self.project_resolution.value[1] :
            error_message = "The Image Resolution must be the same as the project resolution."
            return get_dict()
        required = False
        
        return get_dict()
    
    def __is_different_rect_coordinate(self, area_model: AreaOcrModel, x:int,y:int,w:int,h:int) -> bool:
        if area_model.x.value != x:
            return True
        if area_model.y.value != y:
            return True
        if area_model.w.value != w:
            return True
        if area_model.h.value != h:
            return True
        return False
    
    def update_areas_ocr_section_config(self, area_model:AreaOcrModel) ->None:
        data_dict:dict[str,any] = area_model.to_dict_key_value()
        data_dict.pop("ocr_raw_value")
        data_dict.pop("final_value")
        self.setting_areas.update_section(section=f"{self.section_area_prefix}{area_model.key.value}" ,data_dict=data_dict)
        
    def get_info_setting_areas_file(self) -> dict[str, dict[str, str]]:
        required = True
        completed = False
        error_message = ""
        file_name = Env.NAME_FILE_SETTING_AREAS.value
        section_name = self.section_setting_areas
        areas_models = sorted(self.get_areas_model_new(), key=lambda model: model.key.value)
        total_areas_detected_image:int = len(areas_models)
        total_areas_configured:int = 0
        list_settings_file = self.folder_manager.get_list_path_files(folder=EnvFolders.MAIN_FOLDER, extension=".ini")
        file_path = self.folder_manager.get_file_path(folder=EnvFolders.MAIN_FOLDER, file_name=Env.NAME_FILE_SETTING_AREAS.value)
        warning_areas_ocr = ""
        dict_setting_areas = self.get_dict_setting_areas_file()
        total_areas_sections_ini_file:int = len(dict_setting_areas.keys())
        self.__map_areas_state = {}
        def get_dict():
            dict_data = { section_name : {
                                "required" : str(required),
                                "file_name" :file_name,
                                "completed": str(completed),
                                "total_areas_detected": str(total_areas_detected_image),
                                "total_areas_configured": str(total_areas_configured),
                                "error_message" :error_message,
                                "warning_message":warning_areas_ocr,

                        } }
    
            return  dict_data

        if not file_path in list_settings_file:
            self.setting_areas.save_dict_to_ini(data_dict={})
            
        if total_areas_detected_image > total_areas_sections_ini_file:
            completed = False
            required = True
            
        try:
            for new_area_model in areas_models:
                sub_dictionary = dict_setting_areas.get(f"{self.section_area_prefix}{new_area_model.key.value}", None)
                if not sub_dictionary:
                    self.__map_areas_state[new_area_model.key.value] = False
                    self.update_areas_ocr_section_config(area_model=new_area_model)
                    continue
                key = int(sub_dictionary["key"])
                x = int(sub_dictionary["x"])
                y = int(sub_dictionary["y"])
                w = int(sub_dictionary["w"])
                h = int(sub_dictionary["h"])
                try:
                    name = ast.literal_eval(sub_dictionary["name"])
                except ValueError: 
                    name = sub_dictionary["name"] 
                    
                if  self.__is_different_rect_coordinate(area_model=new_area_model, x=x, y=y, w=w,h=h):
                    self.update_areas_ocr_section_config(area_model=new_area_model)
                    continue
                
                if name :
                        total_areas_configured += 1
                        self.__map_areas_state[key] = True
                else:
                    self.__map_areas_state[key] = False

                
                    
        except Exception :
            error_message = "Fail to read settings area file, Delete setting areas file is recommended"
            return get_dict()
        
        if total_areas_detected_image == total_areas_configured:
            required = False
            completed = True
        
        if total_areas_configured == 0:
            required = True
            completed = False
        
        if self.change_area_image_detected:
            warning_areas_ocr = "[red]![/red] Changes detected in OCR image areas. The area index may change. Testing each area is recommended."        
        
                    
        return get_dict()
         
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
                dict_image_color = AreasOcr.get_color_info_from_image(image_path=file_path)
                self.__hsv_lower_color_area = dict_image_color["hsv_lower_color"]
                self.__hsv_upper_color_area = dict_image_color["hsv_upper_color"]
                required = False
            except Exception as e:
                error_message = str(e)
        link = ""
        if file_path:
            link = self.folder_manager.get_link(path=file_path)
        return { self.section_hsv_color_area : {
                                    "required" : str(required),
                                    "file_name" :file_name,
                                    "hsv_color" : dict_image_color["hsv_color_str"],
                                    "rgb_color" : dict_image_color["rgb_color_str"],
                                    "hex_color" : dict_image_color["hex_color_str"],
                                    "error_message" :error_message,
                                    "image": link,
                                    "folder": self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.HSV_COLOR_AREA),is_path_folder=True) 
                    } }
        

    def create_image_areas_listed(self) -> bool:
        if not self.required_areas_orc_image:
            path_source = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.AREAS_IMAGE_OCR)
            file_name_source = self.folder_manager.get_file_name_from_path(path=path_source)
            file_name_destiny = f"{file_name_source}_listed.png"
            
            path_destiny = self.folder_manager.get_file_path(folder=EnvFolders.AREAS_IMAGE_OCR_LISTED, file_name=file_name_destiny) 
            
            areas, image =  AreasOcr.identify_green_box( file_mask_path=path_source,
                                                            hsv_lower_color_area=self.hsv_lower_area,
                                                            hsv_upper_color_area= self.hsv_upper_area)
            self.project_resolution
            image = AreasOcr.listed_green_box_in_image(image=image, rectangles_map_list=areas)
            AreasOcr.save_image(image=image, file_name_path=path_destiny)
        return True
    
    def get_areas_model_from_file_setting(self)-> list[AreaOcrModel]:        
        """If reading the settings area file fails, return a new list."""
        dict_area_setting = self.setting_areas.load_ini_to_dict()
        list_areas_model = []
        try:
            for section, dict_file_area in  dict_area_setting.items():
                list_areas_model.append(AreaOcrModel.from_dict(dict_map=dict_file_area))
        except Exception as e :
            raise e
            #return self.get_areas_model_new()
            
        return list_areas_model
    
    def get_areas_model_new(self) ->list[AreaOcrModel]:
        file_path = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.AREAS_IMAGE_OCR, only_extension=".png")
        
        list_areas, _ =  AreasOcr.identify_green_box( file_mask_path=file_path,
                                                         hsv_lower_color_area=self.hsv_lower_area,
                                                         hsv_upper_color_area= self.hsv_upper_area)
        
        setting_areas =  AreasOcr.get_list_map_areas_ocr(rectangles_map_list=list_areas)

        return setting_areas
    
    def get_setting_images(self)-> list[dict[str, str|np.ndarray]]:
        list_path_files:list[str] =  self.folder_manager.get_list_path_files(folder=EnvFolders.IMAGES_SETTING_TESTING, extension=".png")
        list_dict_image = []
        try:
            for path in list_path_files:
                dict_image_info = {}
                dict_image_info["name"] = self.folder_manager.get_file_name_from_path(path=path)
                dict_image_info["image"] = AreasOcr.get_image(path)
                dict_image_info["path"] = path
                list_dict_image.append(dict_image_info)
        except:
            pass
        return list_dict_image

    def get_list_sub_image_to_remove_info(self) -> dict[str,dict[str, str]]:
        required = False
        list_img_to_remove = []
        list_path_sub_images_to_remove= self.folder_manager.get_list_path_files(folder=EnvFolders.SUB_IMAGES_TO_REMOVE, extension=".png")
        if list_path_sub_images_to_remove:
            list_img_to_remove = [self.folder_manager.get_file_name_from_path(path= path, without_extension=False) for path in list_path_sub_images_to_remove]
        return { self.section_sub_images_to_remove : {
                                    "required" : str(required),
                                    "images":list_img_to_remove,
                                    "folder": self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.SUB_IMAGES_TO_REMOVE),
                                                                           is_path_folder=True) 
                    } }
        




if __name__ == "__main__":
    # Test 1
    folder_manager = FolderManager(project_name="ift4_starship", screen_id="0_zgh_19-08-2024_ift4_starship_web")
    settings = SettingManager(folder_manager=folder_manager)
    #settings.get_info_image_areas()
    # if not settings.required_areas_orc_image:
    #     settings.create_image_areas_listed()
    # print(settings.get_info_image_areas())
    
    a = settings.get_areas_model_new()
    print(a[0].to_dict_key_value())
    
from dataclasses import dataclass
import re
from types import NoneType
import cv2
import numpy as np
from folder_manager import FolderManager, EnvFolders
from base_class.area_ocr_model import AreaOcrModel
from base_class.name_processor import NameProcessor
from base_class.shared_keys import PropertyCaptureSession, SharedKeys
from typing import get_type_hints

@dataclass
class ImageModel():
        name:str
        path:str 
        image:np.ndarray

@dataclass
class CroppedImageArea():
        key:str
        name:str
        path:str | None
        image:np.ndarray
        area_model:AreaOcrModel


@dataclass
class CaptureSession():
    
    session_id:str
    session_code:str
    is_start_session:bool
    is_end_session:bool
    is_change_detected:bool
    timestamp_seconds:float
    session_captures_number:int
    date:str 
    
    @classmethod
    def validate_properties(cls):
        hints = get_type_hints(cls)
        enum_values = {e.value for e in PropertyCaptureSession}
        
        for prop_name in hints.keys():
            if prop_name not in enum_values:
                raise ValueError(f"Property name '{prop_name}' not found in enum values.")
        
        print(f"All property names are valid according to enum '{PropertyCaptureSession.__name__}'")

class ScreenShotModel(NameProcessor):
        
    key_screen_id = SharedKeys.KEY_SCREEN_ID.value
    key_area_number = SharedKeys.KEY_AREA_NUMBER.value
    key_area_name = SharedKeys.KEY_AREA_NAME.value
    key_group = SharedKeys.KEY_AREA_GROUP.value
    key_value = SharedKeys.KEY_AREA_VALUE.value
    key_raw_value = SharedKeys.KEY_AREA_RAW_VALUE.value
    key_path_image = SharedKeys.KEY_AREA_PATH_IMAGE.value
    key_link_image = SharedKeys.KEY_AREA_LINK_IMAGE.value
    key_image_name_screenshot = SharedKeys.KEY_IMAGE_SCREENSHOT_NAME.value
    key_image_link_screenshot = SharedKeys.KEY_IMAGE_SCREENSHOT_LINK.value
    key_collector_data = SharedKeys.KEY_COLLECTOR_DATA.value
    key_areas_ocr = SharedKeys.KEY_AREAS_OCR.value
        
    
    def __init__(self,
                 folder_manager:FolderManager,
                 screen_id:str,
                 image_source_model:ImageModel,
                 list_area_model:list[AreaOcrModel],
                 capture_session:CaptureSession = None,
                 test_mode:bool = True,
                 save_image_cropped:bool = False,
                 ) -> None:
        NameProcessor.__init__(self=self)
        self.screen_id = screen_id
        self.folder_manager = folder_manager
        self.image_source_model = image_source_model
        self.link_image_source:str = self.folder_manager.get_raw_link(path=image_source_model.path)

        self.list_area_model= list_area_model
        self.capture_session = capture_session
        self.test_mode = test_mode
        self.save_image_cropped = save_image_cropped
    
    def to_final_dict(self):
        image_name_screenshot = self.image_source_model.name
        dict_capture = self.capture_session.__dict__
        shorted_list = self.short_by_group()
        

        list_dict_areas = [{ self.key_area_number:area.key.value,
                             self.key_area_name :area.name.value,
                             self.key_group:area.group_name.value,
                             self.key_value:area.final_value.value,
                            self.key_raw_value:area.ocr_raw_value.value,
                            self.key_path_image:area.path_image_cropped.value,
                            self.key_link_image:area.link_image_cropped.value} for area in shorted_list]
        return {
            self.key_screen_id:self.screen_id,
            self.key_image_name_screenshot:image_name_screenshot,
            self.key_image_link_screenshot:self.link_image_source,
            self.key_collector_data:dict_capture,
            self.key_areas_ocr: list_dict_areas
        }
        
    @staticmethod
    def extract_number(key):
        match = re.search(r'\d+', key)  
        return int(match.group()) if match else float('inf')
    
    @staticmethod
    def extract_number_from_area(area:AreaOcrModel):
        match = re.search(r'\d+', area.name.value)  
        return int(match.group()) if match else float('inf')

    @staticmethod
    def has_numbers(list_names:list[str]) -> bool:
        for name in list_names:
            return bool(re.search(r'\d', name))    

    def grouped_areas(self) -> dict[str, list[AreaOcrModel] | AreaOcrModel]:
        dict_group = {}
        for area in self.list_area_model:
            if area.group_name.value is not None:
                list_areas_grouped:list[AreaOcrModel] =  dict_group.get(area.group_name.value, [])
                list_areas_grouped.append(area)
                dict_group[area.group_name.value] = list_areas_grouped
            else:
                dict_group[area.name.value] = area
                
        sorted_dict_group = dict(sorted(dict_group.items(), key=lambda item: self.extract_number(item[0])))

        return  sorted_dict_group

    
    def short_by_group(self) -> list[AreaOcrModel]:
        list_areas:list[AreaOcrModel] = []
        dict_areas_by_group = self.grouped_areas()
        for key , value in dict_areas_by_group.items():
            if isinstance(value, list):
                list_names = [item.name.value for item in value]
                if self.has_numbers(list_names):
                    inner_list =  sorted(value, key=self.extract_number_from_area)
                else:
                    inner_list = sorted(value, key=lambda area: area.key.value)
                list_areas.extend(inner_list)
            else:
                list_areas.append(value)
        
        return list_areas
    
    def get_basic_dict_areas(self)-> dict[str, any] :
        list_areas:list[AreaOcrModel] = self.short_by_group()
        dict_basic_data:dict[str, any] = {self.get_full_name_area(area, without_n_area=True):area.final_value.value for area in list_areas}
        return dict_basic_data
    
    def get_images_to_process(self, improve_definition:bool = True)->list[CroppedImageArea]:
        list_cropped_img:list[CroppedImageArea] = []
        for area_model in self.list_area_model:
            source_name = self.image_source_model.name.replace(".png", "")
            name = f"source_{source_name}_area_no_{area_model.key.value}"
            path = None
            y = area_model.y.value
            h = area_model.h.value
            x = area_model.x.value
            w = area_model.w.value
            cropped_image = self.image_source_model.image[y:y+h, x:x+w]

            if self.test_mode:
                path = self.folder_manager.get_file_path(folder=EnvFolders.TEMP_FILES, file_name=f"{name}.png")
                cv2.imwrite(path, cropped_image)
                area_model.path_image_cropped.set_value(path)
            elif self.save_image_cropped:
                path = self.folder_manager.get_file_path(folder=EnvFolders.CROPPED_AREAS_OCR, file_name=f"{name}.png")
                cv2.imwrite(path, cropped_image)
                area_model.path_image_cropped.set_value(path)
            
            if improve_definition:
                cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
                kernel = np.array([[0, -0.5, 0],
                   [-0.5, 3, -0.5],
                   [0, -0.7, 0]])
                ksize = (3, 3)  
                sigmaX = 0      
                cropped_image = cv2.GaussianBlur(cropped_image, ksize, sigmaX)
                cropped_image = cv2.filter2D(cropped_image, -1, kernel)
                factor = 2  
                h, w = cropped_image.shape[:2]
                new_height = int(h * factor)
                new_widht = int(w * factor)
                cropped_image = cv2.resize(cropped_image, (new_widht, new_height), interpolation=cv2.INTER_LINEAR)
            
            if path: 
                link = self.folder_manager.get_raw_link(path=path)
                area_model.link_image_cropped.set_value(link)

            cropped_model_image = CroppedImageArea(key=area_model.key.value,
                                                   name=name,
                                                   path=path,
                                                   image=cropped_image,
                                                   area_model=area_model,
                                                   )
            
            list_cropped_img.append(cropped_model_image)
        
        return list_cropped_img
    
    def update_area_model_by_key(self, area_model: 'AreaOcrModel') -> None:
        
        for i, model in enumerate(self.list_area_model):
            if model.key.value == area_model.key.value:
                self.list_area_model[i] = area_model
                return  #
if __name__ == "__main__":
    
    a = CaptureSession(session_id="fdg",
                       session_code="df",
                       session_captures_number=3,
                       is_change_detected=False,
                       is_start_session=True,
                       is_end_session=False,
                       date=None,
                       timestamp_seconds=0.3)
    
    a.validate_properties()
    print(a.__dict__)
    
    
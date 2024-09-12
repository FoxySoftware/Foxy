import ast
from enum import Enum
import re

from base_class.data_processor_enums import StructureType

if __name__ == "__main__":
    from shared_keys import SharedKeys
    from standard_data_model import StandardDataModel
else:
    from base_class.shared_keys import SharedKeys
    from base_class.standard_data_model import StandardDataModel

class AreaType(Enum):
    INTEGER = "Integer"
    STRING = "String"
    DECIMAL = "Decimal" 
    BOOLEAN = "Boolean"
    LIST = "List"
    SET = "Set"
    ANY = "Any"

class AreaOcrModel():
    
    def __init__(self) -> None:
      
        self.key: StandardDataModel = StandardDataModel(type=AreaType.INTEGER.value,
                                                        description="Key of the column",
                                                        required=True,
                                                        key_name_final=SharedKeys.KEY_AREA_NUMBER.value,
                                                        )
        
        self.x: StandardDataModel = StandardDataModel(type=AreaType.INTEGER.value, 
                                                      description="X position", 
                                                      hide=True)
        self.y: StandardDataModel = StandardDataModel(type=AreaType.INTEGER.value, 
                                                      description="Y position", 
                                                      hide=True)
        self.w: StandardDataModel = StandardDataModel(type=AreaType.INTEGER.value, 
                                                      description="W width", 
                                                      hide=True)
        self.h: StandardDataModel = StandardDataModel(type=AreaType.INTEGER.value, 
                                                      description="H height", 
                                                      hide=True)
        
        self.path_image_cropped: StandardDataModel = StandardDataModel(type=AreaType.STRING.value,
                                                                       description="Path of the cropped image file",
                                                                       required=False,
                                                                       hide=True,
                                                                       key_name_final=SharedKeys.KEY_AREA_PATH_IMAGE.value)

        self.link_image_cropped: StandardDataModel = StandardDataModel(type=AreaType.STRING.value,
                                                                description="Link of the cropped image file",
                                                                required=False,
                                                                hide=True,
                                                                key_name_final=SharedKeys.KEY_AREA_LINK_IMAGE.value)
        
        self.name: StandardDataModel = StandardDataModel(type=AreaType.STRING.value,
                                                        description="The name associated with this OCR area.",
                                                        purpose="Identifies or labels the OCR area for reference or processing.",
                                                        input_user=True,
                                                        required=True,
                                                        hide=False,
                                                        key_name_final=SharedKeys.KEY_AREA_NAME.value)
        
        self.group_name: StandardDataModel = StandardDataModel(type=AreaType.STRING.value,
                                                              description="The group name to which this OCR area belongs.",
                                                              purpose="Organizes multiple OCR areas into logical groups for easier management.",
                                                              input_user=True,
                                                              required=True,
                                                              hide=False,
                                                              key_name_final=SharedKeys.KEY_AREA_GROUP.value)
        
        
        self.ocr_raw_value: StandardDataModel = StandardDataModel(type=AreaType.STRING.value,
                                                                  description="Raw OCR value detected from the image.",
                                                                  purpose="Stores the unprocessed text extracted by OCR, useful for debugging or further processing.",
                                                                  hide=False,
                                                                  key_name_final=SharedKeys.KEY_AREA_RAW_VALUE.value)
        
        self.ocr_allow_list: StandardDataModel = StandardDataModel(type=AreaType.SET.value,
                                                                   description="Specifies a set of characters that are allowed for recognition. Only characters included in this list will be considered by the OCR. Characters not in the allowlist will be ignored.",
                                                                   purpose="Limits recognition to a specific set of characters, useful when you know that the text in the image contains only certain characters.",
                                                                   input_user=True,
                                                                   required=False,
                                                                   hide=False)
        
        self.ocr_block_list: StandardDataModel = StandardDataModel(type=AreaType.SET.value,
                                                                  description="Specifies a set of characters to be excluded from recognition. This parameter is ignored if an allowlist is provided.",
                                                                  purpose="Excludes specific characters from the recognized text. It only affects characters that are within the allowlist.",
                                                                  input_user=True,
                                                                  required=False,
                                                                  hide=False)
        
        self.ocr_text_threshold: StandardDataModel = StandardDataModel(type=AreaType.DECIMAL.value,
                                                                   description="A confidence score threshold for including detected text in the results. Only text regions with confidence scores above this threshold will be included. Range: 0 to 1.",
                                                                   purpose="Adjusts the sensitivity of text detection. A higher value means stricter inclusion criteria, while a lower value allows more text with lower confidence.",
                                                                   default=0.2,
                                                                   input_user=True,
                                                                   required=False,
                                                                   hide=False)
        
        self.ocr_low_text: StandardDataModel = StandardDataModel(type=AreaType.SET.value,
                                                            description="A threshold for detecting text in low-quality areas. Defines the minimum confidence score for text detection in regions with blurry or low-quality text. Range: 0 to 1.",
                                                            purpose="Helps in detecting text in challenging conditions. Lower values allow detection in poorer quality text regions, while higher values ensure only clearer text is detected.",
                                                            default=0.4,
                                                            input_user=True,
                                                            required=False,
                                                            hide=False)
        
        self.final_block_list: StandardDataModel = StandardDataModel(type=AreaType.SET.value,
                                                                  description="Specifies a set of characters to be excluded from The final value",
                                                                  purpose="Excludes specific characters from the recognized text to the final text.",
                                                                  input_user=True,
                                                                  required=False,
                                                                  hide=False)
        
        self.type_final_value: StandardDataModel = StandardDataModel(type=AreaType.SET.value,
                                                                   description="Specifies the data type for the final value.",
                                                                   purpose="Defines the type of the final processed value, allowing for different types of output such as string, integer, or decimal.",
                                                                   options={AreaType.STRING.value,
                                                                            AreaType.INTEGER.value,
                                                                            AreaType.DECIMAL.value},
                                                                   
                                                                   default=AreaType.STRING.value,
                                                                   input_user=True,
                                                                   hide=False)
        
        self.final_value: StandardDataModel = StandardDataModel(type=AreaType.ANY.value,
                                                                description="The final value after processing and applying the OCR settings.",
                                                                purpose="Stores the final processed value from the OCR area, based on the selected type_final_value.",
                                                                hide=False,
                                                                required=True,
                                                                key_name_final=SharedKeys.KEY_AREA_VALUE.value)

    @staticmethod
    def get_value_from_type(type:str):

        if type == AreaType.INTEGER.value:
            return StructureType.INTEGER.value
        
        if type == AreaType.DECIMAL.value:
            return StructureType.DECIMAL.value
        
        if type == AreaType.STRING.value:
            return StructureType.STRING.value
        
        return StructureType.STRING.value

    def normalize_space(self) -> None:
        if isinstance(self.ocr_raw_value.value, str):
            final_value_string = re.sub(r'\s+', ' ', self.ocr_raw_value.value).strip()
        
        if isinstance(self.final_block_list.value, list):
            for char in self.final_block_list.value:
                final_value_string = final_value_string.replace(char, "")
            
        self.final_value.set_value(value=final_value_string)
        
        return None
    
    def change_final_value_to_decimal(self):
        """
        Extract the numeric characters (including negative sign) from OCR_raw_value.value
        and convert to float. Handles both comma (,) and dot (.) as decimal separators.
        """
        if isinstance(self.ocr_raw_value.value, str):
            # Replace comma with dot to handle European decimal notation
            str_raw = self.ocr_raw_value.value
            
            if isinstance(self.final_block_list.value, list):
                for char in self.final_block_list.value:
                    str_raw = str_raw.replace(char, "")
                    
            standardized_value = str_raw.replace(',', '.')
            # Remove all characters except digits, dots, and the negative sign
            numeric_string = re.sub(r'[^\d.-]', '', standardized_value)
            # Handle cases with multiple negative signs or dots
            total_sign_negative = numeric_string.count('-')
            total_sign_dot = numeric_string.count('.')
            if total_sign_negative > 1:
                numeric_string.replace(old='-',new="",count= total_sign_negative -1)
            if total_sign_dot > 1:
                numeric_string.replace(old='-',new="",count= total_sign_dot -1)
            try:
                final_value_float = float(numeric_string)
            except ValueError:
                final_value_float = None
            
            self.final_value.set_value(value=final_value_float)
        else:
            self.final_value.set_value(value=None)

        return None

    def change_final_value_to_integer(self):
        """
        Extract numeric characters (including negative sign) from OCR_raw_value.value
        and convert them to an integer.
        """
        if isinstance(self.ocr_raw_value.value, str):
            # Remove all characters except digits and the negative sign
            str_raw = self.ocr_raw_value.value
            
            if isinstance(self.final_block_list.value, list):
                for char in self.final_block_list.value:
                    str_raw = str_raw.replace(char, "")
                    
            numeric_string = re.sub(r'[^\d-]', '', str_raw)
            # Handle cases with multiple negative signs
            total_sign_negative = numeric_string.count('-')
            if total_sign_negative > 1:
                numeric_string.replace(old='-',new="",count= total_sign_negative -1)
           
            try:
                integer_value = int(numeric_string)
            except ValueError:
                integer_value = None
            
            self.final_value.set_value(value=integer_value)
        else:
            self.final_value.set_value(value=None)

        return None

    
 
    def description_to_list(self) -> list[str]:
        list_description = []
        for key in self.__dict__.keys():
            list_description.append(self.__dict__[key].description)
        return list_description
    
    
    def to_dict_key_value(self):
        dict_key_value = {}
        for key in self.__dict__.keys():
            dict_key_value[key] = self.__dict__[key].value
        return dict_key_value
    
    def to_dict_key_value_visible(self):
        dict_key_value = {}
        for key in self.__dict__.keys():
            if not self.__dict__[key].hide:
                dict_key_value[key] = { "input_user": self.__dict__[key].input_user,
                                        "type":self.__dict__[key].type,
                                        "value":self.__dict__[key].value,
                                        "options":self.__dict__[key].options,
                                        "description":self.__dict__[key].description}
                
        return dict_key_value
    
    def get_dict_model_tx(self):
        dict_key_value = {}
        type_final_value:str = None
        for key in self.__dict__.keys():
            if key == "type_final_value":
                type_final_value = self.__dict__[key].value
            if self.__dict__[key].key_name_final:
                    key_final:str = self.__dict__[key].key_name_final
                    if SharedKeys.KEY_AREA_GROUP.value == self.__dict__[key].key_name_final:
                        dict_key_value[SharedKeys.KEY_AREA_GROUP.value] = self.__dict__[key].value
                    
                    elif SharedKeys.KEY_AREA_NAME.value == self.__dict__[key].key_name_final:
                        dict_key_value[SharedKeys.KEY_AREA_NAME.value] = self.__dict__[key].value 
                    else: 
                        dict_key_value[key_final] = self.get_value_from_type(self.__dict__[key].type)
                    

            
        if SharedKeys.KEY_AREA_VALUE.value in dict_key_value:        
            dict_key_value[SharedKeys.KEY_AREA_VALUE.value]= self.get_value_from_type(type_final_value)   
       

        return dict_key_value
    
    @staticmethod
    def from_dict(dict_map:dict[str, any]):
        map_rectangle:AreaOcrModel = AreaOcrModel()
        for key in dict_map.keys():
            try:
                value = ast.literal_eval(dict_map[key])
            except: 
                value = dict_map[key]
            map_rectangle.__dict__[key].set_value(value)
        return map_rectangle
    
    @classmethod
    def key_str_to_list(cls) -> list[str]:
        list_key = []
        for key in cls.__dict__.keys():
            list_key.append(key)
        return list_key
    
    @classmethod
    def count_key(cls):
        return len(cls.key_str_to_list())
    


if __name__ == "__main__":
    
    #Test 1
    # dict_map = {"key": "1", "x":12, "y":24, "w": 100, "h":200 }
    # obj:AreaOcrModel = AreaOcrModel.from_dict(dict_map)
    # obj.ocr_raw_value.set_value("Hola man ! ")
    # print(obj.name.value)
    # print(obj.split_raw_value_char())
    
    #Test 2
    # x = 1
    # y = 2 
    # w = 3
    # h = 4
    # number = 777
    # map_rectangle = AreaOcrModel()
    # map_rectangle.key.set_value(number)
    # map_rectangle.x.set_value(x)
    # map_rectangle.y.set_value(y)
    # map_rectangle.w.set_value(w)
    # map_rectangle.h.set_value(h)
    # map_rectangle.ocr_allow_list.value
    
    # print(map_rectangle)
    # print("_____________")
    # print(map_rectangle.key.value)

    #TEST TX DICT VALUE TYPE .
    a_1 = AreaOcrModel()
    a_2 = AreaOcrModel()  
    
    a_1.key.set_value(1)
    a_1.path_image_cropped.set_value("path_image_cropped")
    a_1.group_name.set_value("group_name")
    a_1.name.set_value("name")
    a_1.ocr_raw_value.set_value("ocr_raw_value")
    a_1.final_value.set_value(4.4)
    a_1.type_final_value.set_value("Decimal")
    
    a_2.key.set_value(2)
    a_2.path_image_cropped.set_value("path_image_cropped")
    a_2.group_name.set_value("group_name")
    a_2.name.set_value("name")
    a_2.ocr_raw_value.set_value("ocr_raw_value")
    a_2.final_value.set_value(8)
    a_2.type_final_value.set_value("Integer") 
     
    
    list_areas = [a_1,a_2]
    for area in list_areas:
        print(area.get_dict_model_tx())
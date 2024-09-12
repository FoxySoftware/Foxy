"""
    MAIN_FOLDER:str = "Projects"  # Folder where all project data/resources are saved
    HSV_COLOR_AREA: str = "4_COLOR_OF_AREAS"  # Image with an HSV color indicating a specific area
    AREAS_IMAGE_OCR:str = "7_AREAS_OCR_IMAGE"  
    IMAGES_SETTING_TESTING:str = "8_TEST_IMAGES"
    CAPTURES: str = "B_CAPTURES_TO_PROCESS_WITH_OCR"  # Folder where all captures or snapshots are saved
    AREAS_IMAGE_OCR_LISTED:str = "C_AREAS_OCR_IMAGE_LISTED"  
    CROPPED_AREAS_OCR: str = "D_CROPPED_IMAGES_OCR"
    OCR_SPREADSHEET:str = "G_DATA_SPREADSHEETS"
    OCR_DATABASE_SQLITE:str = "F_DATA_SQLITE_DATABASES"
    TEMP_FILES: str = "temp_files"
    
    @property
    def value(self):
        return os.environ.get(self.name, self.value)
    
 
    get_list_values:list["Folders"] = lambda: [v for v in Folders if v != Folders.MAIN_FOLDER]

    @property
    def has_session_id(self) -> bool:
        if self == self.CROPPED_AREAS_OCR:
            return True
        if self == self.OCR_SPREADSHEET:
            return True
        if self == self.OCR_DATABASE_SQLITE:
            return True
        if self == self.CAPTURES:
            return True
        return False

"""


from enum import Enum
import os
from pathlib import Path

class Mode(Enum):
    WRITE:str = "WRITE"
    READ:str = "READ"

current_dir = Path(__file__).parent
PATH_CONFIG_FILE = current_dir / '../../config/os_processor_folders.env'
PATH_CONFIG_FILE = PATH_CONFIG_FILE.resolve()


CURRENT_MODE = Mode.WRITE


class EnvFolders(Enum):
    
    MAIN_FOLDER:str = "Projects"  # Folder where all project data/resources are saved
    HSV_COLOR_AREA: str = "4_COLOR_OF_AREAS"  # Image with an HSV color indicating a specific area
    AREAS_IMAGE_OCR:str = "7_AREAS_OCR_IMAGE"  
    IMAGES_SETTING_TESTING:str = "8_TEST_IMAGES"
    CAPTURES: str = "B_CAPTURES_TO_PROCESS_WITH_OCR"  # Folder where all captures or snapshots are saved
    AREAS_IMAGE_OCR_LISTED:str = "C_AREAS_OCR_IMAGE_LISTED"  
    CROPPED_AREAS_OCR: str = "D_CROPPED_IMAGES_OCR"
    OCR_SPREADSHEET:str = "G_DATA_SPREADSHEETS"
    OCR_DATABASE_SQLITE:str = "F_DATA_SQLITE_DATABASES"
    TEMP_FILES: str = "temp_files"
    
    @property
    def value(self):        
        return os.environ.get(self.name, None)

    
    @property
    def has_screen_id(self) -> bool:
        if self == self.CROPPED_AREAS_OCR:
            return True
        if self == self.OCR_SPREADSHEET:
            return True
        if self == self.OCR_DATABASE_SQLITE:
            return True
        if self == self.CAPTURES:
            return True
        return False
    
    
    @classmethod
    def set_as_environment_variables_from_file(cls):

        try:
            with open(PATH_CONFIG_FILE, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if not key:
                                raise ValueError("Empty key found in environment file")
                            os.environ[key] = value
                        except ValueError as ve:
                            print(f"Skipping invalid line '{line}': {ve}")
        except FileNotFoundError:
            raise Exception(f"File '{PATH_CONFIG_FILE}' not found!")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

    @classmethod
    def create_file_env(cls):
        with open(PATH_CONFIG_FILE, 'w') as file:
            for folder in EnvFolders:
                file.write(f"{folder.name}={_default[folder.name].value}\n")
    
    @classmethod
    def list_all_environment_variables(cls):
        for key, value in os.environ.items():
            print(f"{key}={value}")

    get_list_values:list["EnvFolders"] = lambda: [v for v in EnvFolders if v != EnvFolders.MAIN_FOLDER]

    @classmethod
    def get_by_name(cls, name):
        return cls[name]

    

class _default(Enum):

    MAIN_FOLDER:str = "Projects"  # Folder where all project data/resources are saved
    HSV_COLOR_AREA: str = "4_COLOR_OF_AREAS"  # Image with an HSV color indicating a specific area
    AREAS_IMAGE_OCR:str = "7_AREAS_OCR_IMAGE"  
    IMAGES_SETTING_TESTING:str = "8_TEST_IMAGES"
    CAPTURES: str = "B_CAPTURES_TO_PROCESS_WITH_OCR"  # Folder where all captures or snapshots are saved
    AREAS_IMAGE_OCR_LISTED:str = "C_AREAS_OCR_IMAGE_LISTED"  
    CROPPED_AREAS_OCR: str = "D_CROPPED_IMAGES_OCR"
    OCR_SPREADSHEET:str = "G_DATA_SPREADSHEETS"
    OCR_DATABASE_SQLITE:str = "F_DATA_SQLITE_DATABASES"
    TEMP_FILES: str = "temp_files"
    
    
if __name__ == "__main__":
    if CURRENT_MODE == Mode.READ:
        EnvFolders.set_as_environment_variables_from_file()
        EnvFolders.list_all_environment_variables()
    elif CURRENT_MODE == Mode.WRITE:
        EnvFolders.create_file_env()
        EnvFolders.set_as_environment_variables_from_file()
        EnvFolders.list_all_environment_variables()

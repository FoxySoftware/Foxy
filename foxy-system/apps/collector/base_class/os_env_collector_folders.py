from enum import Enum
import os
from pathlib import Path

if __name__ == "__main__":
    from source_mode import SourceMode
else:
    from base_class.source_mode import SourceMode

class Mode(Enum):
    WRITE:str = "WRITE"
    READ:str = "READ"

current_dir = Path(__file__).parent
PATH_CONFIG_FILE = current_dir / '../../config/os_collector_folders.env'
PATH_CONFIG_FILE = PATH_CONFIG_FILE.resolve()


CURRENT_MODE = Mode.READ


class EnvFolders(Enum):
    MAIN_FOLDER = "MAIN_FOLDER"  # Folder where all project data/resources are saved
    VIDEO_SOURCE:str = "VIDEO_SOURCE" # In the case that the project source if a video save the video to process here. 
    START_SESSION_TRIGGER_IMAGE: str = "START_SESSION_TRIGGER_IMAGE"  # Image used to start the image collector process (screenshots)
    END_SESSION_TRIGGER_IMAGE: str = "END_SESSION_TRIGGER_IMAGE"  # Image used to end the image collector process (screenshots)
    LIST_TRIGGER_IMAGES: str = "LIST_TRIGGER_IMAGES"  # Additional images used to trigger a capture
    HSV_COLOR_AREA: str = "HSV_COLOR_AREA"  # Image with an HSV color indicating a specific area
    INTEREST_TRIGGER_AREA: str = "INTEREST_TRIGGER_AREA"  # snapshots with a square or rectangle marked by an HSV/color to indicate where a trigger image can appear
    COMPARISON_AREA: str = "COMPARISON_AREA"  # snapshots with a square or rectangle filled with an HSV color; this area will be monitored, and if a change is detected, the software will take a screenshot
    SCREEN_RECORDING: str = "SCREEN_RECORDING"  # Folder where the screen recording is saved; this video is used to get the necessary snapshots for triggering images and marking areas
    CAPTURES: str = "CAPTURES"  # Folder where all captures or snapshots are saved
    
    @property
    def value(self):        
        return os.environ.get(self.name, None)


    @property
    def has_screen_id(self) -> bool:   
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


    @classmethod
    def get_by_name(cls, name):
        return cls[name]


    def get_list_folders(mode:SourceMode = None)->list["EnvFolders"]:
        list_folder = [v for v in EnvFolders if v != EnvFolders.MAIN_FOLDER]
        if mode is not None:
            if mode == SourceMode.WEB:
                list_folder.remove(EnvFolders.VIDEO_SOURCE)
            elif mode == SourceMode.VIDEO:
                list_folder.remove(EnvFolders.SCREEN_RECORDING)
        return list_folder 
    

class _default(Enum):

    MAIN_FOLDER = "Projects"  # Folder where all project data/resources are saved
    VIDEO_SOURCE:str = "0_VIDEO_SOURCE" # In the case that the project source if a video save the video to process here. 
    START_SESSION_TRIGGER_IMAGE: str = "1_START_IMAGE_SESSION_INDICATOR"  # Image used to start the image collector process (screenshots)
    END_SESSION_TRIGGER_IMAGE: str = "2_END_IMAGE_SESSION_INDICATOR"  # Image used to end the image collector process (screenshots)
    LIST_TRIGGER_IMAGES: str = "3_IMAGES_OF_CAPTURE_INDICATORS"  # Additional images used to trigger a capture
    HSV_COLOR_AREA: str = "4_COLOR_OF_AREAS"  # Image with an HSV color indicating a specific area
    INTEREST_TRIGGER_AREA: str = "5_AREA_OF_INDICATORS"  # snapshots with a square or rectangle marked by an HSV/color to indicate where a trigger image can appear
    COMPARISON_AREA: str = "6_AREA_OF_COMPARISON"  # snapshots with a square or rectangle filled with an HSV color; this area will be monitored, and if a change is detected, the software will take a screenshot
    SCREEN_RECORDING: str = "A_VIDEO_SCREEN_RECORDING"  # Folder where the screen recording is saved; this video is used to get the necessary snapshots for triggering images and marking areas
    CAPTURES: str = "B_CAPTURES_TO_PROCESS_WITH_OCR"  # Folder where all captures or snapshots are saved
    
    
    
if __name__ == "__main__":
    if CURRENT_MODE == Mode.READ:
        EnvFolders.set_as_environment_variables_from_file()
        EnvFolders.list_all_environment_variables()
    elif CURRENT_MODE == Mode.WRITE:
        EnvFolders.create_file_env()
        EnvFolders.set_as_environment_variables_from_file()
        EnvFolders.list_all_environment_variables()

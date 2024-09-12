from PIL import Image
from folder_manager import FolderManager, EnvFolders
from base_class.resolution_dataclass import Resolution
import inquirer


class FileValidation():
    
    def __init__(self, folder_manager:FolderManager, folder:EnvFolders, list_options_to_ignore:list[str]=[], extension_str:str=None, max_image_resolution:Resolution=None) -> None:
        self.folder_manager:FolderManager= folder_manager
        self.max_image_resolution:Resolution= max_image_resolution
        self.folder:EnvFolders = folder
        self.extension_str:str = extension_str
        self.list_options_to_ignore = list_options_to_ignore
        
    def validation_file(self, _, current):
        # Check if the file exists at the specified path
        for option_ignore in self.list_options_to_ignore:
            if current == option_ignore:
                return True
        
        path_file = None
        path_file = self.folder_manager.get_the_recent_file_path(folder=self.folder)
        if not path_file:
            raise inquirer.errors.ValidationError('',    reason=f'The folder is empty. Please save the image in the following directory: {self.folder_manager.get_path(folder=self.folder)}')
        
        if self.extension_str:
            if not path_file.lower().endswith(self.extension_str):
                raise inquirer.errors.ValidationError('', reason=f'The file must have an extension of {self.extension_str}')
        
        if self.max_image_resolution:
            # Check if the image resolution is not larger than resolution 
            try:
                with Image.open(path_file) as img:
                    width, height = img.size
                    if width > self.max_image_resolution.value[0]:
                        raise inquirer.errors.ValidationError('', reason=f'The image resolution exceeds the width of screenshot max width: {self.max_image_resolution.value[0]}')
                    if  height > self.max_image_resolution.value[1]:
                        raise inquirer.errors.ValidationError('', reason=f'The image resolution exceeds the height of screenshot max height: {self.max_image_resolution.value[1]}')

            except Exception as e:
                raise inquirer.errors.ValidationError('', reason=f'Error in the image validation, path {self.folder_manager.get_path(folder=self.folder)} {e}')

        # If all checks pass, return True
        return True
from enum import Enum

if __name__ == "__main__":
    from os_env_processor_folders import EnvFolders
else:
    from processor.base_class.os_env_processor_folders import EnvFolders

END_LINK = "||"

class Link(Enum):

    LINK_FOLDER = "*link_folder *folder:" 
    LINK_IMAGE_SETTING = "*link_image *folder:"
    LINK_FILE_SETTING = "*link_file *folder:"
    LINK_VIDEO = "*link_video *folder:"

    @property
    def get_value(self):
        return self.value
    
    @classmethod
    def create_link_key(cls, type:"Link", folder:EnvFolders|None =None, folder_name:str|None=None)->str:
        if folder:
            return f"{type.value}{folder.name}{END_LINK}"
        elif folder_name:
            return f"{type.value}{folder_name}{END_LINK}"
        raise Exception("Folder or Folder name must be provider")
            
    
    @classmethod
    def get_folder_name(cls, type:"Link", text_with_full_link:str)-> str:
        folder_name = text_with_full_link.split(type.value)[1]
        folder_name = folder_name.split(END_LINK)[0]
        return folder_name
    
    
    
    

if __name__ == "__main__":
    a = Link.create_link_key(type=Link.LINK_FILE_SETTING, folder=EnvFolders.CAPTURES)
    print(f"X {a}X ")
    a = Link.get_folder_name(type=Link.LINK_FILE_SETTING, text_with_full_link=a)
    print(a)

import os
import shutil
import subprocess
import urllib.parse
from pathlib import Path
from typing import  Optional
from base_class.os_env_processor_folders import EnvFolders
from processor.base_class.os_env_geral import OsEnvGeneral as Env

      
class FolderManager:

    def __init__(self, project_name:str, screen_id:str, pasive= False):
        self.__project_name = project_name
        self.__screen_id = screen_id
        self.__main_folder:str = EnvFolders.MAIN_FOLDER.value
        self.project_folder = os.path.join(self.__main_folder, self.__project_name)
        
        if pasive is False:
            
            if Env.UID.value and Env.GID.value:    
                self.create_user_and_group(user_id=Env.UID.value, group_id=Env.GID.value)

            if not os.path.exists(self.project_folder):
                os.makedirs(self.project_folder)
                self.change_permissions(self.__main_folder)

            if self.__screen_id is not None:
                self.create_folder()
            
            
    def create_folder(self):
        list_folder = EnvFolders.get_list_values()

        for folder in list_folder:
            folder_path = self.get_path(folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                self.change_permissions(self.__main_folder)

    def get_path(self, folder:EnvFolders) -> str:
        if folder.value == EnvFolders.MAIN_FOLDER.value:
            return os.path.join(self.__main_folder, self.__project_name)
        if folder.has_screen_id:
            return os.path.join(self.__main_folder, self.__project_name, folder.value, self.__screen_id)
        return os.path.join(self.__main_folder, self.__project_name, folder.value)

    def get_file_path(self, folder: EnvFolders, file_name: str) -> str:
        if folder.has_screen_id:
            return os.path.join(self.__main_folder, self.__project_name, folder.value, self.__screen_id, file_name)
        if folder.value == EnvFolders.MAIN_FOLDER.value:
            return os.path.join(self.__main_folder, self.__project_name, file_name)
        return os.path.join(self.__main_folder, self.__project_name, folder.value, file_name)
    
    def get_the_recent_file_path(self, folder: EnvFolders, only_extension: str = None) -> str | None:
        directory_path = self.get_path(folder=folder)
        most_recent_file = None
        most_recent_time = 0
        
        for entry in os.scandir(directory_path):
            if entry.is_file():
                _, extension = os.path.splitext(entry.name)
                if only_extension:
                    if extension.lower() != only_extension.lower():
                        continue
                mod_time = entry.stat().st_mtime_ns
                if mod_time > most_recent_time:
                    # update the most recent file and its modification time
                    most_recent_file = entry.name
                    most_recent_time = mod_time
                    
        if most_recent_file:
            most_recent_file = os.path.join(directory_path, most_recent_file)
        
        return most_recent_file    

    def get_file_name_from_path(self, path: str, without_extension: bool = True) -> str:
        file_name = os.path.basename(path)
        if without_extension:
            file_name = os.path.splitext(file_name)[0]
        
        return file_name

    def copy_file(self, file_path:str,  folder: EnvFolders):
        directory_destiny:str = self.get_path(folder=folder) 
        os.makedirs(directory_destiny, exist_ok=True)
        file_destiny = os.path.join(directory_destiny, os.path.basename(file_path))
        shutil.copy(file_path, file_destiny)
        self.change_permissions(file_destiny)

    def count_files_with_extension(self, folder: EnvFolders, extension: str) -> int:
        directory_path = Path(self.get_path(folder))
        extension = extension.lower()
        return len([file for file in directory_path.iterdir() if file.is_file() and file.suffix.lower() == extension])
    
    def get_list_path_files(self, folder: EnvFolders, extension: str) -> list[str]:
        directory_path = Path(self.get_path(folder))
        return [ str(file) for file in directory_path.iterdir() if file.is_file() and file.suffix.lower() == extension]
    
    def get_the_last_timestamp_in_folder(self, folder:EnvFolders) -> int:
        path_folder = self.get_path(folder)
        list_file:list[str] = os.listdir(path_folder)
        last_unix_time = 0
        for file_name in list_file:
            if "_" not in file_name:
                continue
            try:
                if int(file_name.split('_')[0]) > last_unix_time:
                    last_unix_time = int(file_name.split('_')[0])
            except Exception:
                pass
        return last_unix_time
    
    def empty_folder(self, folder: EnvFolders) -> None:
        directory_path = Path(self.get_path(folder))
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    @staticmethod
    def path_exists(path) -> bool:
        return Path(path).exists()

    @staticmethod
    def get_last_folder_unix_timestamp(path: str) -> Optional[str]:
        try:
            list_folder:list[str] = [f.name for f in os.scandir(path) if f.is_dir()]
            
            unix_recent_time: int = 0
            last_screen_folder_name: Optional[str] = None
            
            for folder_name in list_folder:
                try:
                    unix_time = int(folder_name.split("_")[0])
                    if unix_time > unix_recent_time:
                        unix_recent_time = unix_time
                        last_screen_folder_name = folder_name
                except ValueError:
                    continue
        except Exception as e:
            print(f"Error to scan the directory: {e}")
            return None
        
        return last_screen_folder_name

    @staticmethod
    def list_folders(directory:str):
        """
        Returns a list of folder names in the specified directory.
        :param directory: Path of the directory to search in.
        :return:list of folder names.
        """
        try:
            # List all files and folders in the given directory
            names = os.listdir(directory)
            # Filter and return only the folders
            folders = [name for name in names if os.path.isdir(os.path.join(directory, name))]
            return folders
        
        except FileNotFoundError:
            print(f"The directory {directory} does not exist.")
            return []
        except PermissionError:
            print(f"You do not have permission to access the directory {directory}.")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    @staticmethod
    def change_permissions(path):
        try:
           a= subprocess.run(['sudo','chmod', '-R', '777', path], check=True, capture_output=True, text=True)
           FolderManager.change_ownership(path=path)
        except subprocess.CalledProcessError as e:
            print(f"Error change permissions: {e}")
    
    @staticmethod
    def change_ownership(path):
        if Env.UID.value and Env.GID.value:    
            try:
                subprocess.run(['sudo', 'chown', '-R', f'{Env.UID.value}:{Env.GID.value}', path], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"Error changing ownership: {e}")
                
    @staticmethod
    def set_foxy_ownership(path):
        try:
            subprocess.run(['sudo', 'chown', '-R', '999:999', path], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error changing ownership: {e}")
   
    @staticmethod
    def create_user_and_group(user_id, group_id):
        try:
            group_exists = subprocess.run(['getent', 'group', str(group_id)], capture_output=True, text=True)
            if group_exists.returncode != 0:
                subprocess.run(['sudo', 'groupadd', '-g', str(group_id), 'newgroup'], check=True)

            user_exists = subprocess.run(['id', str(user_id)], capture_output=True, text=True)
            if user_exists.returncode != 0:
                subprocess.run(['sudo','useradd', '-u', str(user_id), '-g', str(group_id), '-m', 'newuser'], check=True)

        except subprocess.CalledProcessError as e:
            print(f"Error creating user or group: {e}")
        except FileNotFoundError:
            print("Command not found. Ensure `groupadd` and `useradd` are installed.")


    @staticmethod
    def delete_file(file_path:str):
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def get_path_static( folder:EnvFolders, project_name:str) -> str:
        if folder.value == EnvFolders.MAIN_FOLDER.value:
            return os.path.join(folder.value, project_name)
        return os.path.join(EnvFolders.MAIN_FOLDER.value, project_name, folder.value)
    
    
    @staticmethod
    def get_raw_link(path):
        path_source = Env.FOXY_PATH.value

        if Env.OS_HOST.value != "Windows":    
            encoded_path = urllib.parse.quote(path)
            encoded_path_source = urllib.parse.quote(path_source)
            link = f"file://{encoded_path_source}/{encoded_path}"
        else:
            win_path = path.replace("/", "\\")
            if " " in win_path or " " in path_source:
                return f"{path_source}\{win_path}"
            link = f"file://{path_source}\{win_path}"

        return link
    
    @staticmethod
    def get_link(path: str | None, string_link: str = "Open File", is_path_folder: bool = False):
        path_source = Env.FOXY_PATH.value
        
        if not isinstance(path, str):
            return ""
        
        if path.lower().endswith(".png"):
            string_link = string_link.replace("File", "Image 🏞️")
        
        if path.lower().endswith(".mp4") or path.lower().endswith(".avi"):
            string_link = string_link.replace("File", "Video 🎬")
            
        if path.lower().endswith(".ini"):
            string_link = string_link.replace("File", "File 🛠️")
            
        if is_path_folder:
            path = f"{path}/"
            string_link = string_link.replace("File", "Folder 📁")
        
        if Env.OS_HOST.value != "Windows":    
            encoded_path = urllib.parse.quote(path)
            encoded_path_source = urllib.parse.quote(path_source)
            link = f"[link=file://{encoded_path_source}/{encoded_path}]{string_link}[/link]"
        else:
            win_path = path.replace("/", "\\")
            if " " in win_path or " " in path_source:
                return f"{path_source}\{win_path}"
            
            link = f"[link=file://{path_source}\{win_path}]{string_link}[/link]"

        return link
        
    
    
    
if __name__ == "__main__":
    pass
    #folderM = FolderManager(project_name="ift4_starship", session_id="0_zgh_19-08-2024_ift4_starship_web")
    #list_path_test_files = folderM.get_list_path_files(folder=Folders.IMAGES_SETTING_TESTING, extension=".png")
    #print(list_path_test_files)
    #p = folderM.get_the_recent_file_path(folder=Folders.AREAS_IMAGE_OCR_LISTED)
    #folderM.change_permissions(path=p) 
    #a = folderM.get_path(folder=Folders.IMAGES_SETTING_TESTING)
    #print(a)
    #a = Folders.get_by_name(name="CROPPED_AREAS_OCR")
    #print(a.name)
    # a = Folders.CAPTURES.name
    # print(a)
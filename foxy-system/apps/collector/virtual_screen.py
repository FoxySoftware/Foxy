import os
import random
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from xvfbwrapper import Xvfb
from base_class.os_env_collector_folders import EnvFolders
from base_class.resolution_dataclass import Resolution
from folder_manager import FolderManager
from rich import print as rprint
from datetime import datetime
from base_class.source_mode import SourceMode

class VirtualScreen():

    def __init__(self,
                 project_name,
                 current_mode:SourceMode,
                 screen_resolution:Resolution,
                 screen_id:str = None,
                 ) -> None:
        
        self.project_name:str = project_name
        self.web_driver:webdriver.Chrome = None
        self.web_page = ""
        self.screen_id:str = None
        self.pyautogui_library = None
        self.fourcc =None
        self.screen_resolution = screen_resolution
        self.current_mode:SourceMode = current_mode
        return self.init_screen_id(input_screen_id=screen_id)
        
    def init_virtual_screen(self, resolution:Resolution) -> str:
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        display = Xvfb(width=resolution.value[0], height=resolution.value[1])
        display.start()
        # set os environment variable
        os.environ["DISPLAY"] = f":{display.new_display}"
        import pyautogui 
        self.pyautogui_library =pyautogui
        return self.screen_id

    def init_screen_id(self, input_screen_id= None)-> str:
        if not input_screen_id:
            n = 3
            random_string = ''.join(random.choice(["a","b","c","d","f","g","h","y","z"]) for _ in range(n))
            date:str = datetime.now().strftime('%d-%m-%Y')
            prefix = random_string
            suffix:str = self.current_mode.value.lower() 
            name :str= self.project_name.lower()
            number:int = len(FolderManager.list_folders(directory=FolderManager.get_path_static(
                                                        folder=EnvFolders.CAPTURES,
                                                        project_name=self.project_name)))
            
            self.screen_id = f"{number}_{prefix}_{date}_{name}_{suffix}"
        else:
            self.screen_id = input_screen_id
        return self.screen_id
    
    def get_screen_id_from_folders(self) -> str:
        """
        based in the last folder created in SCREENSHOTS.
        update folder_manager
        """
        folder_name = f"{EnvFolders.MAIN_FOLDER.value}/{self.project_name}{EnvFolders.CAPTURES.value}"
        self.screen_id = FolderManager.get_last_folder_unix_timestamp(folder_name)
        self.folder_manager = FolderManager(project_name=self.project_name, screen_id=self.screen_id)
        return self.screen_id
    
    def init_selenium_chrome_service(self) -> tuple[ChromeService, Options]:
        process_name ="Virtual Screen"
        self.current_task = f"{process_name}: init chrome service."
      
        #MARK: Init selenium chrome service
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

        # This is important for some versions of Chrome
        #chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            "--remote-debugging-port=9222")  # This is recommended
        chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
        chrome_service = ChromeService(
            executable_path="/opt/chromedriver/chromedriver-linux64/chromedriver")
        return chrome_service, chrome_options
    
    def start_source_data_driver(self,
                                chrome_service: ChromeService,
                                chrome_options: Options,
                                window_size: Resolution,
                                web_page: str = None,
                                print_task:bool = False
                                )-> webdriver.Chrome:
        #MARK: Start source data driver
        process_name ="Virtual Screen"
        self.current_task = f"{process_name}: init chrome driver."
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.set_window_size(window_size.value[0], window_size.value[1])
        driver.maximize_window()
        self.current_task = f"{process_name}: opening.. {web_page}"
        self.web_page = web_page
        try:
            driver.get(web_page)
            self.current_task = f"{process_name}: {web_page} loaded"
            if print_task:
                rprint(f"[white]{self.current_task}[/white]\n")

        except Exception as e:
            self.current_task = f"[red]{process_name}: Fail to load Web Page: {web_page}[/red]"
            rprint(f"[white]{self.current_task}[/white]\n")

        if "www.youtube.com" in web_page or "youtu.be" in web_page:
            self.current_task = f"{process_name}: Youtube video: {web_page}"
            if print_task:
                rprint(f"[white]{self.current_task}[/white]\n")
                
            video_paused:bool = False
            play_button = None
            try:
                play_button = driver.find_element(By.CLASS_NAME, 'ytp-play-button')
                self.current_task = f"{process_name}: Youtube video: Play button founded"
                if print_task:
                    rprint(f"[white]{self.current_task}[/white]\n")
                
            except Exception :
               pass

            if play_button:
                if "Pause" in play_button.accessible_name:
                    play_button.click() 
                    self.current_task = f"{process_name}: Youtube video: Video paused"
                    video_paused = True
                    if print_task:
                        rprint(f"[white]{self.current_task}[/white]\n")
            try:
                full_screen_button =  driver.find_element(By.CLASS_NAME, 'ytp-fullscreen-button')
                self.current_task = f"{process_name}: Youtube video: Set video to full screen"
                full_screen_button.click()
                if print_task:
                    rprint(f"[white]{self.current_task}[/white]\n")
                
            except Exception:
               pass

            if play_button and video_paused:
                play_button.click()
                self.current_task = f"{process_name}: Youtube video: Video playback resumed"
                if print_task:
                    rprint(f"[white]{self.current_task}[/white]\n")
        
        self.web_driver = driver

    
    def start_chrome_driver_web(self,web_page:str, print_task:bool = False):
        self.init_virtual_screen(self.screen_resolution)
        self.counter_screenshot_per_session = 0
        chrome_service, chrome_options = self.init_selenium_chrome_service()
        
        self.start_source_data_driver(chrome_service,
                                      chrome_options, 
                                      self.screen_resolution,
                                      web_page,
                                      print_task = print_task)
    
    def stop_chrome_driver_web(self) -> bool:
        if self.web_driver:
            self.web_driver.quit()
            return True
        return False
    


    

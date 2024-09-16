import os
import re
import sys

from resource_collector import text_general, text_step_help, text_title
# SET CURRENT PATH PROJECT. 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from base_class.os_env_geral import OsEnvGeneral as Env
from base_class.os_env_collector_folders import EnvFolders as EnvFolders
Env.set_as_environment_variables_from_file()
EnvFolders.set_as_environment_variables_from_file()

import time
import threading
import signal
from rich import print as rprint
from config_manager import ConfigManager
from config_panel import Colors, ConfigProjectPanel, clear_terminal
from custom_event import KeyCtrlZInterrupt
from general_prompts import GeneralPrompts
from image_manager import ImageManager
from base_class.config_sections import ConfigSections
from base_class.os_env_collector_folders import EnvFolders
from base_class.resolution_dataclass import Resolution
from folder_manager import FolderManager
from image_collector import ImageCollector
from base_class.source_mode import SourceMode


class MenuImageCollector(GeneralPrompts):
    available_language = {"English": "EN",
                          "Español": "ES",
                          "Português": "PT"}
    
    def __init__(self) -> None:
        self.init_variables() 
        self.init_strings_options()
        self.flow_control()
        self.is_first_start = True
    
    def init_strings_options(self):
        #MARK: INIT STRING OPTIONS
        self.option_select_language:str =  text_general.map[f'option_select_language_{self.current_language}']
        self.option_welcome:str =  f"{Colors.BLUE}{text_general.map[f'option_welcome_{self.current_language}']}{Colors.BLUE}"
        self.option_stop:str = f"{Colors.RED}{text_general.map[f'option_stop_{self.current_language}']}{Colors.RED}"
        self.option_new_project:str = text_general.map[f"option_new_project_{self.current_language}"]
        self.option_menu_first_recording:str =  text_general.map[f"option_menu_first_recording_{self.current_language}"]
        self.option_menu_recording:str = text_general.map[f"option_menu_recording_{self.current_language}"]
        self.option_existing_project:str = text_general.map[f"option_existing_project_{self.current_language}"]
        self.option_save_new_config:str = text_general.map[f"option_save_config_{self.current_language}"]
        self.option_start_trigger_image:str = text_general.map[f"option_start_trigger_image_{self.current_language}"]
        self.option_end_trigger_image:str = text_general.map[f"option_end_trigger_image_{self.current_language}"]
        self.option_list_trigger_image:str = text_general.map[f"option_list_trigger_image_{self.current_language}"]
        self.option_interest_trigger_area:str = text_general.map[f'option_interest_trigger_area_{self.current_language}']
        self.option_comparison_area:str =  text_general.map[f'option_comparison_area_{self.current_language}']
        self.option_hsv_color_area:str = text_general.map[f'option_hsv_color_area_{self.current_language}']
        self.option_percent_start_trigger:str = text_general.map[f'option_percent_start_trigger_{self.current_language}']
        self.option_percent_end_trigger:str = text_general.map[f'option_percent_end_trigger_{self.current_language}']
        self.option_percent_list_trigger:str = text_general.map[f'option_percent_list_trigger_{self.current_language}']
        self.option_percent_comparison_area:str = text_general.map[f'option_percent_comparison_area_{self.current_language}']
        self.option_show_panel_project:str = text_general.map[f'option_show_panel_project_{self.current_language}']
        self.option_automatic_next:str = text_general.map[f'option_automatic_next_{self.current_language}']
        self.option_menu_video_source:str  = "option_menu_vide_source" # to complete ...

        self._option_default = text_general.map[f"option_default_{self.current_language}"]
        self._option_next = text_general.map[f"option_next_{self.current_language}"]
        self._option_back = text_general.map[f"option_back_{self.current_language}"]
        self._option_cancel = text_general.map[f"option_cancel_{self.current_language}"]
        self._option_back_to_main_menu:str = text_general.map[f'option_back_to_main_menu_{self.current_language}']

        self.option_video_source = text_general.map[f"option_video_source_{self.current_language}"]
        self.option_web_source = text_general.map[f"option_web_source_{self.current_language}"]
        
        # options to show only when the required settings is completed
        self.option_init_main_process:str = text_general.map[f'option_init_main_process_{self.current_language}']
        self.option_menu_session_screen:str = text_general.map[f'option_menu_session_screen_{self.current_language}'] # to complete ...
        section_1 = ConfigSections.PROJECT.value
        section_2 = ConfigSections.SCREEN_RECORDING.value
        section_3 = ConfigSections.VIDEO_SOURCE.value
        section_4 = ConfigSections.START_SESSION_TRIGGER_IMAGE.value
        section_5 = ConfigSections.END_SESSION_TRIGGER_IMAGE.value
        section_6 = ConfigSections.LIST_TRIGGER_IMAGES.value
        section_7 = ConfigSections.INTEREST_TRIGGER_AREA.value
        section_8 = ConfigSections.COMPARISON_AREA.value
        section_9 = ConfigSections.HSV_COLOR_AREA.value
        section_10 = ConfigSections.CAPTURES.value
        
        self.key_menu_section_1 = f"{section_1}_{self.current_language}"
        self.key_menu_section_2 = f"{section_2}_{self.current_language}"
        self.key_menu_section_3 = f"{section_3}_{self.current_language}"
        self.key_menu_section_4 = f"{section_4}_{self.current_language}"
        self.key_menu_section_5 = f"{section_5}_{self.current_language}"
        self.key_menu_section_6 = f"{section_6}_{self.current_language}"
        self.key_menu_section_7 = f"{section_7}_{self.current_language}"
        self.key_menu_section_8 = f"{section_8}_{self.current_language}"
        self.key_menu_section_9 = f"{section_9}_{self.current_language}"
        
        
        options_panel_menu_start =        { f"AUTOMATIC_OPTION_{self.current_language}": self.option_automatic_next,
                                            f"RELOAD_CONFIG_{self.current_language}": self.option_show_panel_project,
                                            self.key_menu_section_1:self.option_welcome}
        
        options_panel_menu_end =          { self.key_menu_section_4: self.option_start_trigger_image,
                                            self.key_menu_section_5: self.option_end_trigger_image,
                                            self.key_menu_section_6: self.option_list_trigger_image,
                                            self.key_menu_section_7: self.option_interest_trigger_area,
                                            self.key_menu_section_8: self.option_comparison_area,
                                            self.key_menu_section_9: self.option_hsv_color_area,

                                            f"MENU_SCREEN_SESSION_{self.current_language}": self.option_menu_session_screen,
                                            f"INIT_MAIN_PROCESS_{self.current_language}": self.option_init_main_process,}

        self.dict_options_panel_menu_web  = {   **options_panel_menu_start,
                                                 self.key_menu_section_2: self.option_menu_recording,
                                                **options_panel_menu_end}

        self.dict_options_panel_menu_video = { **options_panel_menu_start,
                                               #self.key_menu_section_3: self.option_menu_video_source,
                                               **options_panel_menu_end,}
        
        if self.current_mode == SourceMode.WEB:
            self.dict_options_panel_menu = self.dict_options_panel_menu_web
        
        if self.current_mode == SourceMode.VIDEO:
            self.dict_options_panel_menu = self.dict_options_panel_menu_video
    
    @property
    def folder_manager(self) -> FolderManager:
        if not self.__folder_manager:
            self._init_folder_manager()
        return self.__folder_manager
    
    @property
    def config_project_panel(self) -> ConfigProjectPanel:
        if not self.__config_project_panel:
            self._init_config_project()
        return self.__config_project_panel
    
    @property
    def config_manager(self) -> ConfigManager:
        if not self.__config_manager:
            self._init_config_manager()
        return self.__config_manager
    
    def _init_folder_manager(self) -> None:
        self.__folder_manager=FolderManager(project_name=self.project_name, screen_id=None)
        return None
    
    
    def init_variables(self, language:str = "EN", mode:str = SourceMode.WEB):
        #MARK: INIT VARIABLES
        self.is_first_start = False
        self.broadcast_stop_events = threading.Event()
        self.broadcast_pause_events = threading.Event()        
        self._resume_events = threading.Event()
        
        self.current_language = language
        self.project_name:str = None
        self.current_mode:SourceMode = mode
        self.video_source_name:str = None
        self.url:str= None
        self.screen_id:str = None
        self.screen_resolution:Resolution = Resolution.FOUR_K
        self.config_data = {}
        self.process_fps:float = None
        self._duration_capture_process:int = 1e+300
        # video recording
        self.video_seconds_recording = 60
        self.image_collector:ImageCollector = None
        self.list_project_folder:list[str] = self.get_projects_folder()
        self.__folder_manager: FolderManager | None = None
        self.__config_project_panel:ConfigProjectPanel | None = None 
        self.__config_manager:ConfigManager | None = None
        
        
        super().__init__(current_language = language,
                        folder_manager=lambda: self.folder_manager)

    
    
    def _init_config_manager(self):
        self.__folder_manager: FolderManager | None = None
        path_settings:str=self.folder_manager.get_file_path(folder=EnvFolders.MAIN_FOLDER,
                                                            file_name=Env.NAME_FILE_SETTINGS.value)
        self.__config_manager = ConfigManager(path_settings)
    
    def _init_config_project(self):
        self.init_strings_options()
        self.__config_project_panel:ConfigProjectPanel = ConfigProjectPanel(
                                            current_language = self.current_language,
                                            dict_options_menu = self.dict_options_panel_menu,
                                            stop_event = self.broadcast_stop_events,
                                            pause_event = self.broadcast_pause_events,
                                            wakeup_signals = lambda: self.wakeup_signals,
                                            auto_updatable_section = ConfigSections.CAPTURES.value
                                            )
    
    def save_new_config(self, default_next_option:str):
        # MARK: SAVE CONFIG
        if not self.screen_id:
            screen_id = ""
        else: 
            screen_id = self.screen_id

        if not self.process_fps:
            self.process_fps = ""
        if not self.video_source_name:
            self.video_source_name = ""
        folder_link = self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.MAIN_FOLDER),is_path_folder=True)
        if self.current_mode == SourceMode.WEB:
                     
            self.config_data = { ConfigSections.PROJECT.value:
                                            {'language':self.current_language,
                                            'name': self.project_name,
                                            'mode':self.current_mode.value,
                                            'url': f"[link={self.url}]{self.url}[/link]" ,
                                            "screen_id":screen_id,
                                            'screen_resolution': self.screen_resolution.name,
                                            'process_fps':self.process_fps,
                                            'folder':folder_link
                                            },
                                }
            
        if self.current_mode == SourceMode.VIDEO: 
            self.screen_resolution:Resolution = ImageManager.get_resolution_video_source(folder_manager=self.folder_manager)
            self.config_data = { ConfigSections.PROJECT.value:
                                                    {'language':self.current_language,
                                                    'name': self.project_name,
                                                    'mode':self.current_mode.value,
                                                    'video_name':self.video_source_name,
                                                    'screen_id':screen_id,
                                                    'screen_resolution': self.screen_resolution.name,
                                                    'process_fps':self.process_fps,
                                                    'folder':folder_link
                                                    },}
                
        self.config_manager.save_dict_to_ini(self.config_data)  
        return self.flow_control(current_current_option= default_next_option)
    
    def load_config_in_self_variables(self):
        self.config_data = self.config_manager.load_ini_to_dict()
        for section, dict_conf in self.config_data.items():
            if section == "PROJECT":
                self.current_language = dict_conf["language"]
                self.project_name = dict_conf["name"]
                self.current_mode = SourceMode._from_name(dict_conf["mode"])
                self.screen_id = dict_conf["screen_id"]
                screen_resolution_name:str = dict_conf.get("screen_resolution", None)
                
                if screen_resolution_name:
                    self.screen_resolution = Resolution.from_string(screen_resolution_name)
                self.process_fps =  dict_conf["process_fps"]
                self.url = dict_conf.get("url", None)
                if self.url:
                    pattern = r'\[link=[^\]]+\](http[s]?://[^\[]+)\[/link\]'
                    match = re.search(pattern, self.url)
                    self.url = match.group(1)
                self.video_source_name = dict_conf.get("video_name", None)
    
    def load_show_panel_config(self, default_next_option:str):

        clear_terminal()
        #preload
        self.load_config_in_self_variables()
        self.init_image_collector() 
        #full load settings
        self.load_config_in_self_variables() 
        self.init_strings_options()        
        
        
        panel_1 = ConfigSections.PROJECT.value
        if self.current_mode == SourceMode.WEB:
            panel_2 = ConfigSections.SCREEN_RECORDING.value
        elif self.current_mode == SourceMode.VIDEO:
            panel_2 = ConfigSections.VIDEO_SOURCE.value
        panel_3 = ConfigSections.START_SESSION_TRIGGER_IMAGE.value
        panel_4 = ConfigSections.END_SESSION_TRIGGER_IMAGE.value
        panel_5 = ConfigSections.LIST_TRIGGER_IMAGES.value
        panel_6 = ConfigSections.INTEREST_TRIGGER_AREA.value
        panel_7 = ConfigSections.COMPARISON_AREA.value
        panel_8 = ConfigSections.HSV_COLOR_AREA.value
        panel_9 = ConfigSections.CAPTURES.value

        only_sections = [panel_1, panel_2, panel_3, panel_4, panel_5, panel_6, panel_7, panel_8, panel_9]
        data_config_only_sections = {}
        
        for key, value in self.config_data.items():
            if key  in  only_sections:
                data_config_only_sections[key] = value
    
        self.config_data = data_config_only_sections
        default_next_option = self.config_project_panel.show_panel(self.config_data)
        self.flow_control(current_current_option=default_next_option)
    
    def update_variables_options_threshold(self):
        if self.image_collector is not None:
            self.option_percent_start_trigger:str = self.option_percent_start_trigger.replace("*threshold", f"{self.image_collector.threshold_similarity_start_percent} %")
            self.option_percent_end_trigger:str =  self.option_percent_end_trigger.replace("*threshold", f"{self.image_collector.threshold_similarity_end_percent} %")
            self.option_percent_list_trigger:str =  self.option_percent_list_trigger.replace("*threshold", f"{self.image_collector.threshold_similarity_list_percent} %")
            self.option_percent_comparison_area:str =  self.option_percent_comparison_area.replace("*threshold", f"{self.image_collector.threshold_difference_comparison_area_percent} %")
        


    
    def menu_save_config(self, default_next_option:str, others_options:list[str]) -> str :    
        # MARK: MENU SAVE OPTIONS

        option_selected:str = self.prompt_options(default_option=default_next_option,
                                    others_options=others_options,
                                    message=text_general.map[f"option_save_config_{self.current_language}"])
        if option_selected == default_next_option:
            self.save_new_config(default_next_option=default_next_option)
        return option_selected
    
    def menu_new_project(self, default_next_option:str ) -> str:
        # MARK: MENU NEW PROJECT

        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")
        
        if self.is_first_start == False:
            self.init_variables(language=self.current_language, mode=self.current_mode)
            self.init_strings_options()
            
        self.list_project_folder = self.get_projects_folder()
        self.project_name = self.prompt_string_name_value(ask=text_general.map[f"message_name_project_{self.current_language}"], 
                                                          existing_names=self.list_project_folder)
                
   
        option = self.prompt_options(default_option=None, others_options=[self.option_video_source, self.option_web_source], 
                                     message= "Select a source" )
        
        if option == self.option_web_source:
            self.current_mode = SourceMode.WEB
            self.url = self.prompt_string_url(ask=text_general.map[f"message_url_project_{self.current_language}"])
             
        elif option ==  self.option_video_source: 
            self.current_mode = SourceMode.VIDEO
            
            option = self.prompt_options_file(dict_text_help=text_step_help.help_video_source,
                                     folder=EnvFolders.VIDEO_SOURCE,
                                     extension_str=".mp4", 
                                     option_to_validate=self._option_next,
                                     others_options=[ self._option_back, self._option_cancel],
                                     max_image_resolution=None,
                                      message= text_general.map[f"message_to_continue_{self.current_language}"])
            

            if option == self._option_back:
                self.folder_manager.remove_folder(folder=EnvFolders.MAIN_FOLDER)
                self.__folder_manager = None
                self.menu_new_project(default_next_option=default_next_option)
            
            if option == self._option_cancel:
                self.folder_manager.remove_folder(folder=EnvFolders.MAIN_FOLDER)
                sys.exit(0)
                
                
            default_next_option = self.option_start_trigger_image
            
            
            path = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.VIDEO_SOURCE, only_extension=".mp4")
            self.video_source_name = self.folder_manager.get_file_name_from_path(path=path, without_extension=False)
        
        self.is_new_project:bool = True
        return self.save_new_config(default_next_option=default_next_option)
    
    def menu_session_screen(self) -> str:
        # MARK: MENU SESSION SCREEN

        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")
        title = text_general.map[f"title_menu_session_screen_{self.current_language}"]
        description = text_general.map[f"help_menu_session_screen_{self.current_language}"]
        rprint(f"[green]{title}[/green]")
        rprint(f"[white]{description}\n[/white]")
        option_1 = text_general.map[f"ask_create_new_session_screen_{self.current_language}"]
        option_2 = text_general.map[f"ask_select_a_session_screen_{self.current_language}"]
        option_3 = text_general.map[f"ask_delete_a_session_screen_{self.current_language}"]
        message = text_general.map[f"message_to_continue_{self.current_language}"]
        selected_option = self.prompt_options(default_option=option_1,
                                                   others_options= [
                                                                    #option_2,
                                                                    #option_3,
                                                                    self.option_show_panel_project], 
                                                   message= message)

        if selected_option == option_1:
            clear_terminal()
            rprint(f"[green]{text_title.title}[green]")
            message = text_general.map[f"message_new_session_created_{self.current_language}"]
            self.new_screen_session()
            message = message.replace("*screen_id", self.screen_id)
            rprint(f"[green]{message}[/green]")
            time.sleep(2)
        
        return self.option_show_panel_project

    def menu_screen_recording(self, dict_text_help:dict[str, str], others_options:list[str] = [], select_resolution:bool =True )-> str:
        #MARK: MENU SCREEN RECORDING
        if select_resolution:
            _result = self.prompt_resolution(dict_text_help=dict_text_help,
                                            others_options=others_options)
            
            if isinstance(_result, Resolution):
                self.screen_resolution = _result
            else:
                return _result
        
        _result = self.prompt_seconds_video()
        self.video_seconds_recording =_result
        self.init_image_collector()
        self.start_record_video()
        return  self.option_show_panel_project
    

    def flow_control(self, current_current_option:str =None):
        # MARK: FLOW CONTROL
        if not current_current_option:
            current_step = self.option_welcome
        else:
            current_step = current_current_option
        self.step_actions:dict[str:callable] = None
        
        def load_step_actions():
            
            self.step_actions = {
                self.option_select_language: self.select_language,
                self.option_welcome: lambda: self.prompt_welcome(new_project=self.option_new_project,
                                                            select_project=self.option_existing_project, list_projects = self.list_project_folder),
                
                self.option_save_new_config: lambda: self.save_new_config(default_next_option=self.option_welcome),
                self.option_show_panel_project: lambda: self.load_show_panel_config(default_next_option=self.option_automatic_next),
                self.option_new_project: lambda: self.menu_new_project(default_next_option=self.option_menu_first_recording),
                
                self.option_existing_project: self.handle_existing_project,
                self.option_automatic_next: self.automatic_next_required_step,
                self.option_menu_first_recording: lambda: self.menu_screen_recording(dict_text_help=text_step_help.help_resolution_and_video_recording,
                                                                                    others_options=[self.option_show_panel_project,
                                                                                                    self.option_welcome, self.option_stop]),

                self.option_menu_recording: lambda: self.menu_screen_recording(dict_text_help=text_step_help.help_video_recording,
                                                                            others_options=[self.option_show_panel_project,
                                                                                            self.option_welcome, self.option_stop],
                                                                            select_resolution=False),
                # key_menu_section_4
                self.option_start_trigger_image: lambda: self.prompt_options_file(dict_text_help=(text_step_help.help_start_trigger_image_web 
                                                                                                    if self.current_mode == SourceMode.WEB 
                                                                                                    else text_step_help.help_start_trigger_image_video),
                                                                                    message=text_general.map[f"message_to_continue_{self.current_language}"],
                                                                                    option_to_validate=self.option_automatic_next,
                                                                                    others_options=[self.option_show_panel_project,
                                                                                                    self.option_percent_start_trigger,
                                                                                                    self.option_welcome, 
                                                                                                    self.option_stop],
                                                                                    folder=EnvFolders.START_SESSION_TRIGGER_IMAGE,
                                                                                    extension_str=".png",
                                                                                    list_remove_i_after_validate=self.config_project_panel.red_options,
                                                                                    key_item=self.key_menu_section_4,
                                                                                    
                                                                                ),
                #key_menu_section_5
                self.option_end_trigger_image: lambda: self.prompt_options_file(dict_text_help=text_step_help.help_end_trigger_image,
                                                                    message=text_general.map[f"message_to_continue_{self.current_language}"],
                                                                    option_to_validate=None,
                                                                    others_options=[self.option_automatic_next,
                                                                                    self.option_show_panel_project,
                                                                                    self.option_percent_end_trigger,
                                                                                    self.option_list_trigger_image, 
                                                                                    self.option_welcome, self.option_stop], 
                                                                    folder=EnvFolders.END_SESSION_TRIGGER_IMAGE,
                                                                    extension_str=".png"),
                
                self.option_list_trigger_image: lambda: self.prompt_options_file(dict_text_help=text_step_help.help_list_trigger_image,
                                                                    message=text_general.map[f"message_to_continue_{self.current_language}"],
                                                                    option_to_validate=None,
                                                                    others_options=[self.option_automatic_next,
                                                                                    self.option_show_panel_project,
                                                                                    self.option_interest_trigger_area,
                                                                                    self.option_percent_list_trigger,
                                                                                    self.option_welcome, self.option_stop], 
                                                                    folder=EnvFolders.LIST_TRIGGER_IMAGES,
                                                                    extension_str=".png"),
                #key_menu_section_7
                self.option_interest_trigger_area: lambda: self.prompt_options_file(dict_text_help=text_step_help.help_interest_trigger_area,
                                                                        message=text_general.map[f"message_to_continue_{self.current_language}"],
                                                                        option_to_validate=self.option_automatic_next,
                                                                        others_options=[self.option_show_panel_project,
                                                                                        self.option_welcome, self.option_stop],
                                                                        folder=EnvFolders.INTEREST_TRIGGER_AREA, 
                                                                        extension_str=".png",
                                                                        list_remove_i_after_validate=self.config_project_panel.red_options,
                                                                        key_item=self.key_menu_section_7,
                                                                        ),
                #key_menu_section_8
                self.option_comparison_area: lambda: self.prompt_options_file(dict_text_help=text_step_help.help_area_comparison,
                                                                    message=text_general.map[f"message_to_continue_{self.current_language}"],
                                                                    option_to_validate=self.option_automatic_next,
                                                                    others_options=[self.option_show_panel_project,
                                                                                    self.option_percent_comparison_area,
                                                                                    self.option_welcome, self.option_stop],
                                                                    folder=EnvFolders.COMPARISON_AREA,
                                                                    extension_str=".png",
                                                                    list_remove_i_after_validate=self.config_project_panel.red_options,
                                                                    key_item=self.key_menu_section_8,),
                
                self.option_hsv_color_area: lambda: self.prompt_options_file(dict_text_help=text_step_help.help_hsv_color_area,
                                                                message=text_general.map[f"message_to_continue_{self.current_language}"],
                                                                option_to_validate=self.option_automatic_next,
                                                                others_options=[self.option_show_panel_project,
                                                                                self.option_welcome, self.option_stop],
                                                                folder=EnvFolders.HSV_COLOR_AREA, extension_str=".png",
                                                                ),
                
                self.option_percent_start_trigger: lambda: self.handle_percent_trigger(ConfigSections.START_SESSION_TRIGGER_IMAGE.value,
                                                                                    title_percent_key="title_percent_start_trigger",
                                                                                    help_percent_key="help_percent_start_trigger",
                                                                                    ask_percent_key="ask_percent_start_trigger",
                                                                                    option_key="threshold_similarity_%"),
                
                self.option_percent_end_trigger: lambda: self.handle_percent_trigger(ConfigSections.END_SESSION_TRIGGER_IMAGE.value,
                                                                                    title_percent_key="title_percent_end_trigger",
                                                                                    help_percent_key="help_percent_end_trigger",
                                                                                    ask_percent_key="ask_percent_end_trigger",
                                                                                    option_key="threshold_similarity_%"),
                
                self.option_percent_list_trigger: lambda: self.handle_percent_trigger(ConfigSections.LIST_TRIGGER_IMAGES.value,
                                                                                    title_percent_key="title_percent_list_trigger",
                                                                                    help_percent_key="help_percent_list_trigger",
                                                                                    ask_percent_key="ask_percent_list_trigger",
                                                                                    option_key="threshold_similarity_%"),
                
                self.option_percent_comparison_area: lambda: self.handle_percent_trigger(ConfigSections.COMPARISON_AREA.value,
                                                                                        title_percent_key="title_percent_comparison_area",
                                                                                        help_percent_key="help_percent_comparison_area",
                                                                                        ask_percent_key="ask_percent_comparison_area",
                                                                                        option_key="threshold_difference_%"),
                
                self.option_menu_session_screen:lambda: self.menu_session_screen(),
                self.option_init_main_process: self.init_thread_collector_process,
                self.option_stop: sys.exit
            }
        
        load_step_actions()

        while True:
            
            try:
                if current_step in self.step_actions:
                    if current_step in  {self.option_start_trigger_image,
                                                  self.option_end_trigger_image,
                                                  self.option_list_trigger_image,
                                                  self.option_comparison_area}:
                        
                        self.update_variables_options_threshold()
                        load_step_actions()
                        
                    current_step = self.step_actions[current_step]()
                    
            except KeyboardInterrupt:
                #print("Flow contrl KeyboardInterrupt")
                self.wakeup_signals()
                current_step = None
                break
            except KeyCtrlZInterrupt:
                #print("Flow contrl KeyCtrlZInterrupt")
                self.wakeup_signals()
                current_step = None
                break
            except Exception as e:
                raise e
            
        if self.project_name  and self.screen_id:
            self.flow_control(current_current_option=self.option_show_panel_project)
        else:
            sys.exit(0)

    def handle_existing_project(self):
        if self.is_first_start == False:
            self.init_variables(language=self.current_language, mode=self.current_mode)
            self.init_strings_options()    
        self.get_projects_folder()
        option_selected = self.prompt_options(default_option=None, others_options=[*self.list_project_folder,
                                                                                        self.option_welcome,
                                                                                        self.option_stop],
                                                   message=text_general.map[f"select_project_folder_{self.current_language}"])
        
        if option_selected in self.list_project_folder:
            self.project_name = option_selected
            return self.option_show_panel_project
        return option_selected

    def get_projects_folder(self):
        _list_project_folder = FolderManager.list_folders(directory=EnvFolders.MAIN_FOLDER.value)
        self.list_project_folder = []
        for folder_project in _list_project_folder:
            try:
                _folder_manager = FolderManager(project_name=folder_project, screen_id=None, pasive=True)
                
                path_setting_file:str= _folder_manager.get_file_path(folder=EnvFolders.MAIN_FOLDER,
                                                                file_name=Env.NAME_FILE_SETTINGS.value)
                
                exist_setting_file_exist:bool = FolderManager.path_exists(path=path_setting_file)
                if exist_setting_file_exist:
                    __config_manager = ConfigManager(path_setting_file)
                    __config_data = __config_manager.load_ini_to_dict()
                    
                    dict_project_section = __config_data.get(ConfigSections.PROJECT.value, None)
                    if isinstance(dict_project_section, dict):
                        _current_language = dict_project_section.get("language", None)
                        _project_name = dict_project_section.get("name", None)
                        _current_mode = dict_project_section.get("mode", None)
                        _screen_resolution_name:str = dict_project_section.get("screen_resolution", None)
                    else:
                        continue
                    if not None in {_current_language, _project_name, _current_mode, _screen_resolution_name}:
                        if not _current_language in [*self.available_language.values()]:
                            continue
                        try:
                            SourceMode._from_name(name=_current_mode)
                        except:
                            continue
                        self.list_project_folder.append(folder_project)
            except Exception as e:
                print(f"Fail to load Project Folders. {e}.")
                    
        return self.list_project_folder 
    
    @staticmethod    
    def split_float_number(num):
        int_part, decimal_part = str(num).split(".")
        return int(int_part), int(decimal_part)
    
    def handle_percent_trigger(self, section, option_key, title_percent_key:str, help_percent_key:str, ask_percent_key:str) :
        print(section)
        value = self.prompt_ask_float_value(
            title=text_general.map[f"{title_percent_key}_{self.current_language}"],
            help=text_general.map[f"{help_percent_key}_{self.current_language}"],
            ask=text_general.map[f"{ask_percent_key}_{self.current_language}"]
        )
        self.config_manager.update_section(section=section, options={option_key: value})
        return self.option_show_panel_project

    def init_thread_collector_process(self):
        if self.current_mode == SourceMode.WEB:
            minute_seconds =self.prompt_ask_float_value( title= text_general.map[f"title_duration_capture_process_{self.current_language}"],
                                                         help= text_general.map[f"help_duration_seconds_{self.current_language}"],
                                                         main_title=False,
                                                         ask=text_general.map[f"ask_minute_seconds_{self.current_language}"],
                                        minimum=0, limit=11340, round_value=False)
            if float(minute_seconds) == 0.0:
                self._duration_capture_process = 1e+300
            else:
                minute, seconds = self.split_float_number(num=minute_seconds)
                self._duration_capture_process = minute * 60 + seconds
            
        threads = self.parallel_process()
        self.wait_for_processes(threads)
        self.config_manager.update_section(section=self.config_project_panel.auto_updatable_section,
                                           options=self.config_project_panel.last_data_update)
        self._clear_all_events()
        return self.option_show_panel_project
    

    
    def select_language(self):
        selection = self.prompt_options(
           default_option=None,
            others_options=[*self.available_language.keys(), self.option_welcome, self.option_stop],
            message=text_general.map[f"message_select_language_{self.current_language}"])
        
        if selection == self.option_welcome or selection == self.option_stop:
            return selection
        
        if selection in self.available_language:
            self.init_variables(language=self.available_language[selection], mode=self.current_mode)
            self.init_strings_options()
            self.flow_control()
        
        return self.option_welcome
        
    def automatic_next_required_step(self) -> str:
        # MARK:AUTOMATIC NEXT
        if self.config_project_panel.red_options:
            next_option:str = self.dict_options_panel_menu[self.config_project_panel.red_options[0]] 
            return next_option
        else:
            return self.option_show_panel_project
   
    def init_image_collector(self):
        # MARK:INIT IMAGE COLLECTOR
        rprint(f"[white]{text_general.map[f'starting_message_{self.current_language}']}[white]")
        self.image_collector = ImageCollector(self.project_name,
                                              current_language = self.current_language,
                                              screen_id = self.screen_id,
                                              screen_resolution = self.screen_resolution,
                                              current_mode =self.current_mode,
                                              video_source_name = self.video_source_name,
                                              stop_event = self.broadcast_stop_events,
                                              pause_event = self.broadcast_pause_events,
                                              
                                              )
        
        if not self.screen_id: 
            self.screen_id = self.image_collector.screen_id
            self.config_manager.update_section(section=ConfigSections.PROJECT.value,
                                               options={"screen_id":self.screen_id})

    def new_screen_session(self):
        self.screen_id = None
        self.init_image_collector()
        
                
    def get_fps_of_current_settings(self):
        self.image_collector.start_chrome_driver_web(self.url, print_task=True)
        fps = self.image_collector.record_screen(test_mode=True)
        self.image_collector.stop_chrome_driver_web()
        self.process_fps = fps
        self.config_manager.update_section(section=ConfigSections.PROJECT.value,
                                           options={"process_fps":self.process_fps})
        return
        
    def start_record_video(self):
        # MARK:START VIDEO RECORDING
        if not self.image_collector:
            raise Exception("initialize image collector first")
        message = text_general.map[f"virtual_screen_initialized_{self.current_language}"]
        rprint(f"[white]{message}{self.url}[white]")
        if not self.process_fps:
            self.get_fps_of_current_settings()
        self.image_collector.start_chrome_driver_web(self.url)
        
        self.image_collector.record_screen(duration_seconds=self.video_seconds_recording, desired_fps=float(self.process_fps))
        self.image_collector.stop_chrome_driver_web()
    
    def start_main_process(self):
        # MARK:START MAIN PROCESS
        if not self.image_collector:
            raise Exception("initialize image collector first")
        if self.current_mode == SourceMode.WEB:
            self.image_collector.start_chrome_driver_web(self.url)
            self.image_collector.main_process(timer_process_seconds=self._duration_capture_process)
            self.image_collector.stop_chrome_driver_web()
        elif self.current_mode == SourceMode.VIDEO:
            self.image_collector.main_process()
            
    def _only_stop_event(self):
        #clear others.
        self._resume_events.clear()
        self.broadcast_pause_events.clear()
        # »stop
        self.broadcast_stop_events.set()
        time.sleep(1)
        self._clear_all_events()
    
    def _only_pause_event(self):
        #clear others.
        self._resume_events.clear()
        self.broadcast_stop_events.clear()
        # »pause
        self.broadcast_pause_events.set()
    

    def _only_resume_event(self):
        #clear others.
        self.broadcast_pause_events.clear()
        self.broadcast_stop_events.clear()
        #»resume
        self._resume_events.set()
 
    def _clear_all_events(self):
        self.broadcast_pause_events.clear()
        self.broadcast_stop_events.clear()
        self._resume_events.clear()

    def wait_for_processes(self,threads):
        for thread in threads:
            thread.join()
        
    def parallel_process(self) -> tuple[threading.Thread]:
        self.wakeup_signals()
        process_thread_1 = threading.Thread(target=self.start_main_process, daemon=True)
        
        process_thread_2 = threading.Thread(target=self.config_project_panel.update_automatic_layout,
                                            kwargs={"function_return_dict":self.image_collector.capture_session_info},
                                            daemon=True)

        process_thread_1.start()
        process_thread_2.start()

        return process_thread_1, process_thread_2
    

    def handle_signal(self, signal_number, frame):
        #print(f"signal {signal_number}")
        if signal_number == 2 or signal_number == 15: #stop
            if not self.broadcast_stop_events.is_set():
                self._only_stop_event()

        elif signal_number != 2 and signal_number != 15: #pause o resume
            if  self.broadcast_pause_events.is_set(): # currently paused
                self._only_resume_event()
            else:
                self._only_pause_event()

    
    def wakeup_signals(self):
        signal.signal(signal.SIGINT, self.handle_signal)# 2: Interrupt (Ctrl + C) - Internal function Stop process
        signal.signal(signal.SIGTERM, self.handle_signal)  # 15:  Internal function Stop process
        signal.signal(signal.SIGTSTP, self.handle_signal) # 20: (Ctrl + Z) - Internal Continue - Resumes suspended process
        signal.signal(signal.SIGCONT, self.handle_signal)# 19 or 18: Internal Continue - Resumes suspended process

if __name__ == "__main__":
    MenuImageCollector()

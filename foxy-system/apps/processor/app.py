import os
import sys
from api.gateway.rabbitmq import RabbitMQ


# SET CURRENT PATH PROJECT. 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import signal
import threading
import time
import uuid
from rich import print as rprint
from custom_event import KeyCtrlZInterrupt
from data_processor import DataProcessor
from image_processor import ImageProcessor
from menu_areas import MenuAreas
from config_panel import ConfigProjectPanel
from ocr_processor import OcrProcessor
from base_class.sections import ConfigSections
from base_class.menu_project import ConfigMenuProject
from base_class.shared_keys import SharedKeys
from setting_area_panel import SettingAreaPanel
from settings_manager import SettingManager
from resource_processor import text_general, text_step_help, text_title
from api.gateway.rabbitmq_env import COLLECTOR_MODULE_SOURCE, PROCESSOR_MODULE_SOURCE, RabbitMqEnv
from folder_manager import FolderManager, EnvFolders
from base_class.os_env_geral import OsEnvGeneral as Env
from base_class.source_mode import SourceMode
from rich.panel import Panel

Env.set_as_environment_variables_from_file()
EnvFolders.set_as_environment_variables_from_file()


def clear_terminal():
    # Linux
    os.system("clear")
   
class MenuImageCollector(MenuAreas):
    
    available_language = {"English": "EN", "Español": "ES", "Português": "PT"}
    
    def __init__(self) -> None:
        self.init_variables()
        self.init_strings_options()
        self.flow_control()
        self._is_first_init:bool = True

    def init_strings_options(self):
        #MARK: INIT STRING OPTIONS
        self.option_select_project:str = "option_select_project" 
        self.option_select_a_session:str = "option_select_a_session"
        self.option_load_area_ocr_image: str = "option_load_area_ocr_image"
        self.option_init_ocr_process:str = "option_init_ocr_process"
        self.option_menu_data_process:str = "option_menu_data_process"
        self.option_enable_disable_gpu_ocr: str = "option_enable_disable_gpu_ocr"
        
        self.option_export_database:str = text_general.map[f'option_export_database_{self.current_language}']
        self.option_export_existent_database:str = text_general.map[f'option_export_existing_database_{self.current_language}']
        self.option_export_spreadsheet:str = text_general.map[f'option_export_spreadsheet_{self.current_language}']
        self.option_clear_processed_queue:str = text_general.map[f'option_clear_processed_queue_{self.current_language}']


        self.option_stop:str = f"|↩ {text_general.map[f'option_stop_{self.current_language}']}"
        self.option_back:str = text_general.map[f'option_back_{self.current_language}']

        menu_1 = ConfigMenuProject.AUTOMATIC_OPTION.value
        menu_2 = ConfigMenuProject.RELOAD_CONFIG.value
        menu_3 = ConfigMenuProject.WELCOME.value
        menu_4 = ConfigMenuProject.AREAS_IMAGE_OCR.value
        menu_5 = ConfigMenuProject.SETTING_AREAS_OCR.value
        menu_6 = ConfigMenuProject.INIT_OCR_PROCESS.value
        menu_7 = ConfigMenuProject.MENU_DATA_PROCESS.value
        menu_8 = ConfigMenuProject.EXIT.value
        menu_9 = ConfigMenuProject.ACTIVATE_GPU.value

        
        options_panel_menu_start =        { f"{menu_1}_{self.current_language}": self.option_automatic_next,
                                            f"{menu_2}_{self.current_language}": self.option_show_panel_project,
                                            f"{menu_3}_{self.current_language}":self.option_select_project,
                                            f"{menu_4}_{self.current_language}":self.option_load_area_ocr_image,
                                            f"{menu_5}_{self.current_language}": self.option_main_setting_area,

                                            f"{menu_9}_{self.current_language}": self.option_enable_disable_gpu_ocr,
                                            }
        
        options_panel_menu_end =          { f"{menu_6}_{self.current_language}": self.option_init_ocr_process,
                                            f"{menu_7}_{self.current_language}": self.option_menu_data_process,
                                            #f"{menu_8}_{self.current_language}": self.option_stop
                                            }

        self.dict_options_panel_menu = {**options_panel_menu_start, **options_panel_menu_end}
        self.message_checks_set_1 = text_general.map[f"message_checks_set_1_{self.current_language}"] 
        self.message_checks_set_2 = text_general.map[f"message_checks_set_2_{self.current_language}"]
        self.message_use_keys =text_general.map[f"message_use_keys_{self.current_language}"] 
        #SET CHECKS 1 
        self.lang_timestamp_seconds =  text_general.map[f"timestamp_seconds_{self.current_language}"]
        self.lang_session_code = text_general.map[f"session_code_{self.current_language}"]
        self.lang_is_start_session =  text_general.map[f"is_start_session_{self.current_language}"]
        self.lang_is_end_session = text_general.map[f"is_end_session_{self.current_language}"]
        self.lang_is_change_detected =  text_general.map[f"is_change_detected_{self.current_language}"]
        self.lang_session_captures_number = text_general.map[f"session_captures_number_{self.current_language}"]
        self.lang_date =  text_general.map[f"date_{self.current_language}"]
        #SET CHECKS 2
        self.lang_area_key_number = text_general.map[f"area_key_number_{self.current_language}"]
        self.lang_area_key_raw_value =  text_general.map[f"area_key_raw_value_{self.current_language}"]
        self.lang_area_key_link_image =  text_general.map[f"area_key_link_image_{self.current_language}"]
        #OTHERS OPTIONS
        self.option_default = text_general.map[f"option_default_{self.current_language}"]
        self.option_next = text_general.map[f"option_next_{self.current_language}"]
        self.option_back = text_general.map[f"option_back_{self.current_language}"]
        self.option_cancel = text_general.map[f"option_cancel_{self.current_language}"]
        
    
    def init_variables(self, language:str = "EN"):
        #MARK: INIT VARIABLES
        self._is_first_init = False
        self.id_instance = str(uuid.uuid4())
        self.id_instance_collector_consume = f"{self.id_instance}_{COLLECTOR_MODULE_SOURCE}"
        self.id_instance_processor_consume = f"{self.id_instance}_{PROCESSOR_MODULE_SOURCE}"
        self.broadcast_stop_events = threading.Event()
        self.broadcast_pause_events = threading.Event()        
        self._resume_events = threading.Event()
        self.current_language = language
        self.project_selected:str = None
        self.list_screen_session:list[str] = []
        self.screen_id_selected: str = None
        self.list_screen_id_with_no_folder: list[str] = []
        
      

        self.list_project_folder:list[str] = FolderManager.list_folders(directory=EnvFolders.MAIN_FOLDER.value)
        self.rabbit_mq_env:RabbitMqEnv = RabbitMqEnv(
                                                     host=Env.RABBITMQ_HOST.value,
                                                     username=Env.RABBITMQ_USERNAME.value,
                                                     password=Env.RABBITMQ_PASSSWORD.value,
                                                     port=Env.RABBITMQ_PORT.value,
                                                     exchange_name=Env.RABBITMQ_EXCHANGE.value
                                                     )
        self.__current_lang_ocr = "en"
        self.__active_gpu_ocr:bool = False
        self.__folder_manager: FolderManager | None = None
        self.__setting_manager: SettingManager | None= None
        self.__config_project_panel:ConfigProjectPanel | None= None
        self.__setting_area_panel: SettingAreaPanel | None = None
        self.__ocr_processor:OcrProcessor | None = None
        self.__image_processor:ImageProcessor | None= None
        self.__data_processor:DataProcessor | None= None

        
        super().__init__(   current_language = self.current_language,
                            available_language = self.available_language,
                            folder_manager=lambda: self.folder_manager,
                            setting_manager=lambda: self.setting_manager,
                            setting_area_panel =lambda: self.setting_area_panel,
                            ocr_processor =lambda: self.ocr_processor ) 
        
    @property
    def data_processor(self) -> DataProcessor:
        if not self.__data_processor:
            self.init_data_processor()
        return self.__data_processor

    @property
    def image_processor(self) -> ImageProcessor:
        if not self.__image_processor:
            self.init_image_processor()
        return self.__image_processor
    
    @property
    def ocr_processor(self) -> OcrProcessor:
        if not self.__ocr_processor:
            self.init_ocr_processor()
            
        if (self.__ocr_processor.lang_mode != self.__current_lang_ocr or 
            self.__ocr_processor.active_gpu != self.__active_gpu_ocr):
            self.init_ocr_processor()
        return self.__ocr_processor
            
    @property
    def folder_manager(self) -> FolderManager:
        if not self.__folder_manager:
            self.init_folder_manager()
        return self.__folder_manager
   
    @property
    def setting_manager(self) -> SettingManager: 
        if not self.__setting_manager:
            self.init_setting_manager()
        return self.__setting_manager
        
    @property
    def setting_area_panel(self) -> SettingAreaPanel: 
        if not self.__setting_area_panel:
            self.init_setting_area_panel()
        return self.__setting_area_panel
    
    @property
    def config_project_panel(self) -> ConfigProjectPanel: 
        if not self.__config_project_panel:
            self.init_config_project_panel()
        return self.__config_project_panel
    
    def init_folder_manager(self) -> None:
        self.__folder_manager= FolderManager(project_name=self.project_selected, screen_id=self.screen_id_selected)
        return None
    
    def init_setting_manager(self) -> None:
        self.__setting_manager = SettingManager(folder_manager=self.folder_manager,
                                                screen_id = self.screen_id_selected,
                                                image_processor = lambda: self.image_processor)
        return None
    
    def init_setting_area_panel(self) -> None:
        self.__setting_area_panel = SettingAreaPanel(available_language=self.available_language,
                                              folder_manager=self.folder_manager, )
        return None
    
    def init_config_project_panel(self) -> None:
        self.__config_project_panel = ConfigProjectPanel(current_language = self.current_language,
                                            dict_options_menu = self.dict_options_panel_menu,
                                            stop_event = self.broadcast_stop_events,
                                            pause_event = self.broadcast_pause_events,
                                            auto_updatable_section = ConfigSections.TASK_IN_PROGRESS.value,
                                            wakeup_signals = lambda: self.wakeup_signals
                                            )
        
        return None
    
    def init_ocr_processor(self,) -> None:
        self.__active_gpu_ocr = self.setting_manager.gpu_ocr
        self.__ocr_processor = OcrProcessor(folder_manager= self.folder_manager,
                                            lang_area_model=self.__current_lang_ocr,
                                            active_gpu = self.__active_gpu_ocr)
        return None
    
    def init_image_processor(self):
        queue_name:str = self.rabbit_mq_env.get_queue_name(filter_module_source=COLLECTOR_MODULE_SOURCE, screen_id=self.screen_id_selected)
        routing_key:str = self.rabbit_mq_env.get_routing_key_name(filter_module_source=COLLECTOR_MODULE_SOURCE, screen_id=self.screen_id_selected)
        
        self.__image_processor = ImageProcessor(
                                                stop_event = self.broadcast_stop_events,
                                                pause_event = self.broadcast_pause_events,
                                                project_name = self.project_selected,
                                                session_id = self.screen_id_selected,
                                                host = self.rabbit_mq_env.host,
                                                exchange = self.rabbit_mq_env.exchange_name,
                                                username = self.rabbit_mq_env.username,
                                                password = self.rabbit_mq_env.password,
                                                routing_key = routing_key,
                                                queue_name = queue_name,
                                                id_instance_collector_consume = self.id_instance_collector_consume,
                                                folder_manager = lambda: self.folder_manager,
                                                setting_manager = lambda: self.setting_manager,
                                                ocr_processor = lambda: self.ocr_processor)
        return None
    
    def init_data_processor(self):
        queue_name:str = self.rabbit_mq_env.get_queue_name(filter_module_source=PROCESSOR_MODULE_SOURCE, screen_id=self.screen_id_selected)
        routing_key:str = self.rabbit_mq_env.get_routing_key_name(filter_module_source=PROCESSOR_MODULE_SOURCE, screen_id=self.screen_id_selected)
        
        self.__data_processor = DataProcessor(
                                                project_name = self.project_selected,
                                                screen_id = self.screen_id_selected,
                                                current_language = self.current_language,
                                                available_language = self.available_language,
                                                stop_event = self.broadcast_stop_events,
                                                host = self.rabbit_mq_env.host,
                                                exchange = self.rabbit_mq_env.exchange_name,
                                                username = self.rabbit_mq_env.username,
                                                password = self.rabbit_mq_env.password,
                                                routing_key = routing_key,
                                                queue_name = queue_name,
                                                folder_manager = lambda: self.folder_manager,
                                                setting_manager = lambda: self.setting_manager,)
        return None


    def show_panel_project(self):
        self.setting_manager.check_update_config()
        data_config = self.setting_manager.get_dict_setting_file()
        panel_1 = ConfigSections.PROJECT.value
        panel_2 = ConfigSections.HSV_COLOR_AREA.value
        panel_3 = ConfigSections.AREAS_IMAGE_OCR.value
        panel_4 = ConfigSections.AREAS_IMAGE_OCR_LISTED.value
        panel_5 = ConfigSections.SECTION_SETTING_AREAS_OCR.value
        panel_6 = ConfigSections.PROJECT_SESSION_STATE.value
        panel_7 = ConfigSections.TASK_IN_PROGRESS.value
        only_sections = [panel_1, panel_2, panel_3, panel_4, panel_5, panel_6, panel_7]
        data_config_only_sections = {}
        
        for key, value in data_config.items():
            if key  in  only_sections:
                data_config_only_sections[key] = value
            
        next_option = self.config_project_panel.show_panel(config_data= data_config_only_sections)
        return next_option
    
    
    def menu_select_project(self)-> str:
        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")
        rprint("")
        if not self._is_first_init:
            self.init_variables()
            self.init_strings_options()
        self.list_project_folder = FolderManager.list_folders(directory=EnvFolders.MAIN_FOLDER.value)
        option_selected = self.prompt_options(default_option=None, 
                                                   others_options=[*self.list_project_folder,
                                                                    self.option_stop],
                                                   message=text_general.map[f"select_project_folder_{self.current_language}"])
        
        if option_selected == self.option_stop:
            return self.option_stop
        
        if option_selected in self.list_project_folder:
            self.project_selected = option_selected

        return self.option_select_a_session
    
    def menu_select_session(self) -> str:
        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")
        rprint("")
        self.load_collector_sessions()
        option_selected = self.prompt_options(default_option=None,
                                                   others_options=[*self.list_screen_session,
                                                                    self.option_back],
                                                   message=text_general.map[f"select_project_session_{self.current_language}"]
                                                   )
        if option_selected == self.option_back:
            return self.option_select_project
        
        if option_selected in self.list_screen_session:
            self.screen_id_selected = option_selected
            return self.option_show_panel_project
        
                    
        return option_selected
    
    
    def wakeup_signals(self):
        signal.signal(signal.SIGINT, self.handle_signal)# 2: Interrupt (Ctrl + C) - Internal function Stop process
        signal.signal(signal.SIGTERM, self.handle_signal)  # 15:  Internal function Stop process
        signal.signal(signal.SIGTSTP, self.handle_signal) # 20: (Ctrl + Z) - Internal Continue - Resumes suspended process
        signal.signal(signal.SIGCONT, self.handle_signal)# 19 or 18: Internal Continue - Resumes suspended process


    def flow_control(self):
        # MARK: FLOW CONTROL
        current_step = self.option_select_project
        
        step_actions = {
            self.option_enable_disable_gpu_ocr:self.menu_gpu_ocr,
            self.option_select_project: self.menu_select_project,
            self.option_select_a_session: self.menu_select_session,
            self.option_show_panel_project: self.show_panel_project,
            self.option_load_area_ocr_image: lambda: self.prompt_options_file(dict_text_help=text_step_help.help_areas_ocr,
                                                                    message=text_general.map[f"message_to_continue_{self.current_language}"],
                                                                    option_to_validate=self.option_automatic_next,
                                                                    others_options=[self.option_show_panel_project,
                                                                                    self.option_stop],
                                                                    folder=EnvFolders.AREAS_IMAGE_OCR,
                                                                    max_image_resolution=self.setting_manager.project_resolution,
                                                                    extension_str=".png",
                                                                    list_remove_i_after_validate=self.config_project_panel.red_options,
                                                                    key_item=f"{ConfigSections.AREAS_IMAGE_OCR.value}_{self.current_language}" ,
                                                                    key_item_2=f"{ConfigSections.AREAS_IMAGE_OCR_LISTED.value}_{self.current_language}"
                                                                    ),
            self.option_main_setting_area:self.menu_main_setting_areas,
            self.option_automatic_next: self.automatic_next_required_step,
            self.option_init_ocr_process: self.init_threads_ocr_process,
            self.option_menu_data_process: self.menu_data_export,
            self.option_stop: sys.exit
        }

        while True:
            try:
                if current_step in step_actions:
                    current_step = step_actions[current_step]()
            except KeyboardInterrupt:
                self.wakeup_signals()
                current_step = None
                break
            except KeyCtrlZInterrupt:
                self.wakeup_signals()
                current_step = None
                break
            except Exception as e:
                raise e
            #     break

        if self.project_selected  and self.screen_id_selected:
            current_step = self.option_show_panel_project
            self.flow_control()
        else:
            sys.exit(0)  


    def menu_data_export(self):
        #MARK: DATA EXPORT
        SUFFIX_DB = ".sqlite"
        SUFFIX_XLSX = ".xlsx"

        list_db_files = self.folder_manager.get_list_path_files(folder=EnvFolders.OCR_DATABASE_SQLITE, extension=SUFFIX_DB)
        
        list_db_name_files = [self.folder_manager.get_file_name_from_path(path=path_file,
                                                                       without_extension=False) for path_file in list_db_files]
        
        
        list_xlsx_files = self.folder_manager.get_list_path_files(folder=EnvFolders.OCR_SPREADSHEET, extension=SUFFIX_XLSX)
        
        list_name_xlsx_files = [self.folder_manager.get_file_name_from_path(path=path_file,
                                                                       without_extension=False) for path_file in list_xlsx_files]
        options_export = [self.option_export_database, 
                          self.option_export_existent_database,
                          self.option_export_spreadsheet,
                          self.option_clear_processed_queue,
                          self.option_back]
        
        if not list_db_name_files:
            options_export.remove(self.option_export_existent_database)
            
        option_selected = self.prompt_options(default_option=None, others_options=options_export)
        
        # option back 
        if option_selected == self.option_back:
            return self.option_show_panel_project
        
        db_name:str|None = None
        new_database:bool = True
        over_write = False
        xlsx_name:str|None = None  
        # export a new database
        if option_selected == self.option_export_database:
            db_name = self.prompt_string_name_value(ask=text_general.map[f"option_write_database_name_{self.current_language}"],
                                                      suffix=SUFFIX_DB,
                                                      existing_names=list_db_name_files,
                                                      return_with_suffix=True)
            if "cancel" in db_name.lower():
                return self.option_menu_data_process
            
        # export a existent db
        if option_selected == self.option_export_existent_database:
            db_name = self.prompt_options(default_option=None,
                                          others_options=list_db_name_files,
                                          message=text_general.map[f"message_to_continue_{self.current_language}"] )
            new_database = False
            
            option_over_write = self.prompt_options(default_option=None,
                                          others_options=["Yes", "No", "Cancel"],
                                          message=text_general.map[f"message_overwrite_db_{self.current_language}"])
            
            if option_over_write == "Yes":
                over_write = True
            elif option_over_write == "No":
                over_write = False
            elif option_over_write == "Cancel":
                return self.option_menu_data_process
                
        # export spreadsheet
        if option_selected == self.option_export_spreadsheet:
            xlsx_name = self.prompt_string_name_value(ask=text_general.map[f"message_write_a_spreadsheet_name_{self.current_language}"],
                                                    suffix=SUFFIX_XLSX,
                                                    existing_names=list_name_xlsx_files,
                                                    return_with_suffix=True)

            if "cancel" in xlsx_name.lower():
                return self.option_menu_data_process
        # option clear queue
        if option_selected == self.option_clear_processed_queue:
            option_purgue_queue = self.prompt_options(default_option=None,
                                          others_options=[self.option_automatic_next, "Cancel"],
                                          message="")
            
            if option_purgue_queue == self.option_automatic_next:
                self.data_processor.purge_queue_processed(self.option_clear_processed_queue)
                return self.option_menu_data_process
            elif option_purgue_queue == "Cancel":
                return self.option_menu_data_process
            
            

        
            
        key_session_code = SharedKeys.KEY_SESSION_CODE.value  # 'session_code'
        key_is_start_session = SharedKeys.KEY_IS_START_SESSION.value  # 'is_start_session'
        key_is_end_session = SharedKeys.KEY_IS_END_SESSION.value  # 'is_end_session'
        key_is_change_detected = SharedKeys.KEY_IS_CHANGE_DETECTED.value  # 'is_change_detected'
        key_timestamp_seconds = SharedKeys.KEY_TIMESTAMP_SECONDS.value  # 'timestamp_seconds'
        key_session_captures_number = SharedKeys.KEY_SESSION_CAPTURES_NUMBER.value  # 'session_captures_number'
        key_date = SharedKeys.KEY_DATE.value  # 'date'
        
        key_area_number = SharedKeys.KEY_AREA_NUMBER.value # in tx×
        key_area_raw_value = SharedKeys.KEY_AREA_RAW_VALUE.value # in tx×
        key_area_link_image = SharedKeys.KEY_AREA_LINK_IMAGE.value # in tx×
        
        map_dict_vars = {self.lang_timestamp_seconds:key_timestamp_seconds ,
                        self.lang_session_code:key_session_code,
                        self.lang_is_start_session:key_is_start_session,
                        self.lang_is_end_session:key_is_end_session,
                        self.lang_is_change_detected:key_is_change_detected,
                        self.lang_session_captures_number:key_session_captures_number,
                        self.lang_date:key_date,
                        self.lang_area_key_number:key_area_number,
                        self.lang_area_key_raw_value:key_area_raw_value,
                        self.lang_area_key_link_image:key_area_link_image}
        
        map_dict_sets = {self.message_checks_set_1:SharedKeys.KEYS_TO_UNPACK_IN_TX.value ,
                        self.message_checks_set_2:SharedKeys.TX_THIRD_INDEX_DIMENSION.value,
                        }
        
        
        def translation_options_to_var(dict_result:dict[str, str]):
            var_dict = {}
            for _set, value in dict_result.items():
                list_var = []
                key_set = map_dict_sets[_set]
                for var in value:                
                    list_var.append(map_dict_vars[var])    
                var_dict[key_set] = list_var
            return var_dict
            
                    
        dict_defaults = {self.message_checks_set_1:[],
                        self.message_checks_set_2: []}
        
        
        unpack_in_tx = [self.lang_session_code,
                        self.lang_is_start_session,
                        self.lang_is_end_session,
                        self.lang_is_change_detected,
                        self.lang_session_captures_number,
                        self.lang_date]
        
        if self.setting_manager.project_source_type == SourceMode.WEB:
            unpack_in_tx.append(self.lang_timestamp_seconds)
            
        dict_columns = {self.message_checks_set_1: unpack_in_tx,
                        self.message_checks_set_2: [ self.lang_area_key_number,
                                                    self.lang_area_key_raw_value,
                                                    self.lang_area_key_link_image]}
                
        prompt_check = self.prompt_checks(dict_set_checks=dict_columns,
                                                    dict_set_defaults=dict_defaults,
                                                    message= self.message_use_keys,
                                                    default_check_str=self.option_default,
                                                    back_option=self.option_back,
                                                    cancel_option=self.option_cancel,
                                                    next_option=self.option_next)
        
        if not prompt_check:
            return self.option_menu_data_process
        else:
            dict_tx_options = translation_options_to_var(dict_result=prompt_check)
                        
        if option_selected == self.option_export_spreadsheet:
            self.data_processor.start_data_export_spreadsheet(xlsx_nane=xlsx_name,
                                                              dict_tx_options=dict_tx_options,
                                                              option_str=option_selected)
            
            path_folder = self.folder_manager.get_path(folder=EnvFolders.OCR_SPREADSHEET)
            panel_link = Panel(f"SpreedSheet Folder: {self.folder_manager.get_link(path=path_folder, is_path_folder=True)}",
                               title=xlsx_name, style="white", title_align="left")
            print("")
            rprint(panel_link)   
        else:    
            self.data_processor.start_data_export_database(db_name=db_name,
                                                        dict_tx_options=dict_tx_options,
                                                            option_str=option_selected,
                                                            new_database=new_database,
                                                            over_write=over_write)
            
            path_folder = self.folder_manager.get_path(folder=EnvFolders.OCR_DATABASE_SQLITE)
            panel_link = Panel(f"DataBase Folder: {self.folder_manager.get_link(path=path_folder, is_path_folder=True)} ",
                               title=db_name, style="white", title_align="left")
            print("")
            rprint(panel_link)
            
        return self.option_menu_data_process

    def handle_signal(self, signal_number, frame):
        #print(f"signal {signal_number}")
        if signal_number == 2 or signal_number == 15:
            if not self.broadcast_stop_events.is_set():
                self.broadcast_stop_events.set()
                
        elif signal_number != 2 and signal_number != 15:
            if not self.broadcast_pause_events.is_set():
                self.broadcast_pause_events.set()
                self._resume_events.clear()
                
            else:
                self._resume_events.set()
                self.broadcast_pause_events.clear()

    
    def init_threads_ocr_process(self):
        threads = self.collector_process()
        self.wakeup_signals()
        self.wait_for_processes(threads)
        return  self.option_show_panel_project
    
    def wait_for_processes(self,threads):
        for thread in threads:
            thread.join()
    
    def _handler_repose_collector_task(self):
        while not self.broadcast_stop_events.is_set():
            if self._resume_events.is_set():
                self.broadcast_pause_events.clear()
                self.image_processor.reassume_consume_collector()
            time.sleep(1)
        self.image_processor.stop_consume_collector()
        return
    
    def collector_process(self) -> tuple[threading.Thread]:
        process_thread_1 = threading.Thread(target=self.start_collector_consume, daemon=True)
        process_thread_2 = threading.Thread(target=self.config_project_panel.update_automatic_layout,
                                            kwargs={"function_return_dict":self.image_processor.get_current_task_properties}, daemon=True)
        process_thread_3 = threading.Thread(target=self._handler_repose_collector_task, daemon=True)
        process_thread_1.start()
        process_thread_2.start()
        process_thread_3.start()

        return process_thread_1, process_thread_2, process_thread_3
    
    # def export_data_to_db(self) -> tuple[threading.Thread]:
    #     process_thread_1 = threading.Thread(target=self., daemon=True)
    #     process_thread_1.start()

    #     return process_thread_1

    def load_collector_sessions(self) -> list[str]:
        routing_keys:list[str] = self.rabbit_mq_env.get_list_routing_keys(filter_project_name=self.project_selected, filter_module_source="collector")
        self.list_screen_session = [routing_key.split(f"{Env.RABBITMQ_PREFIX_ROUTING_KEY_COLLECTOR.value}_")[1] for routing_key in routing_keys]
        self.check_if_queue_has_folder()
        self.delete_queue_with_no_folder()
        if self.list_screen_id_with_no_folder:
            for screen_id in self.list_screen_id_with_no_folder:
                self.list_screen_session.remove(screen_id)
        return self.list_screen_session
    
    def check_if_queue_has_folder(self):
        self.list_screen_id_with_no_folder = []

        for session in self.list_screen_session:
            folder_manager = FolderManager(project_name=self.project_selected, screen_id=session, pasive=True)
            try:
                _path = folder_manager.get_path(folder=EnvFolders.CAPTURES)
                exist_folder = folder_manager.path_exists(path=_path)
                if not exist_folder :
                    self.list_screen_id_with_no_folder.append(session)
            except Exception as e:
                self.list_screen_id_with_no_folder.append(session)
                

    def delete_queue_with_no_folder(self):
        try:
            rabbit_mq = RabbitMQ(
                host=self.rabbit_mq_env.host,
                username=self.rabbit_mq_env.username,
                password=self.rabbit_mq_env.password,
                exchange=self.rabbit_mq_env.exchange_name_encoded,
                queue_name=None,
                routing_key=None
            )
            rabbit_mq._connect_active()
            rabbit_mq._create_channel_active()
            
            for session_screen_in in self.list_screen_id_with_no_folder:
                # COLLECTOR QUEUE 
                collector_queue_name = self.rabbit_mq_env.get_queue_name(filter_module_source=COLLECTOR_MODULE_SOURCE, screen_id=session_screen_in)
                queue_exist = rabbit_mq._queue_exists(collector_queue_name)
                if queue_exist:
                    rabbit_mq._active_channel.queue_delete(queue=collector_queue_name)
                # PROCESSOR QUEUE
                processor_queue_name = self.rabbit_mq_env.get_queue_name(filter_module_source=PROCESSOR_MODULE_SOURCE, screen_id=session_screen_in)
                queue_exist = rabbit_mq._queue_exists(processor_queue_name)
                if queue_exist:
                    rabbit_mq._active_channel.queue_delete(queue=processor_queue_name)

        except Exception as e:
            print(f"Fail to delete queue {e}")
        finally:
            rabbit_mq.close_active_connection()
    
    def automatic_next_required_step(self) -> str:
        if self.config_project_panel.red_options:
            next_option:str = self.dict_options_panel_menu[self.config_project_panel.red_options[0]] 
            return next_option
        else:
            return self.option_show_panel_project
   
   
    def menu_gpu_ocr(self):
        option_enable_gpu = text_general.map[f"option_activate_gpu_{self.current_language}"]
        option_disable_gpu = text_general.map[f"option_disable_gpu_{self.current_language}"]
        message_gpu = text_general.map[f"message_gpu_ocr_{self.current_language}"]
        selected_option = self.prompt_options(default_option=None, others_options=[option_enable_gpu,
                                                                                   option_disable_gpu,
                                                                                   self.option_back],
                                              message= message_gpu)
        
        if selected_option == self.option_back:
            return self.option_show_panel_project
        if selected_option == option_enable_gpu:
            self.setting_manager.update_gpu_ocr(gpu_ocr=True)
            self.init_ocr_processor()
        elif selected_option == option_disable_gpu:
            self.setting_manager.update_gpu_ocr(gpu_ocr=False)
            self.init_ocr_processor()

        return self.option_show_panel_project
    
    def start_collector_consume(self):
        self.image_processor.start_consume_collector()
        
    
        
if __name__ == "__main__":
    
    MenuImageCollector()

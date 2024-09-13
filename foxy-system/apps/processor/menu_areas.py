import os
import copy
import re
from types import NoneType
from menu_panel_areas import PanelArea
from processor.base_class.name_processor import SET_SYMBOL
from settings_manager import SettingManager
from folder_manager import FolderManager
from base_class.area_ocr_model import AreaOcrModel
from resource_processor import text_general, text_step_help


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def clear_terminal():
    # Linux
    os.system("clear")
    
MIDDLE_SYMBOL = " ➔ "

class MenuAreas(PanelArea):
    def __init__(self, **kwargs) -> None:
        
        self.current_language:str = kwargs.get("current_language", "EN")
        self.available_language:dict[str,str] = kwargs["available_language"]
        self._folder_manager:callable =  kwargs["folder_manager"]
        self._setting_manager:callable = kwargs["setting_manager"]
        self._setting_area_panel:callable  = kwargs["setting_area_panel"]
        
        super().__init__( **kwargs)

        self.option_main_setting_area:str = "option_settings_map_areas"
        self.option_show_panel_project:str = text_general.map[f'option_show_panel_project_{self.current_language}']
        
        self.option_back_to_main_menu:str = text_general.map[f'option_back_to_main_menu_{self.current_language}']

        # name area 
        self.option_menu_set_name_area:str = f"{Colors.GREEN}1:{Colors.RESET} {text_general.map[f'option_menu_set_name_area_{self.current_language}']}" 
        self.option_set_name_area:str =  text_general.map[f'option_set_name_area_{self.current_language}'] 
        # group name 
        self.option_menu_set_group_name_area:str = f"{Colors.GREEN}2:{Colors.RESET} {text_general.map[f'option_menu_set_group_name_area_{self.current_language}']}"
        self.option_set_group_name_area:str = text_general.map[f'option_set_group_name_area_{self.current_language}']
        self.option_create_a_new_group:str = text_general.map[f"option_create_a_new_group_{self.current_language}"]
        # allow list ocr
        self.option_menu_allow_list_ocr:str = f"{Colors.GREEN}3:{Colors.RESET} {text_general.map[f'option_menu_allow_list_ocr_{self.current_language}']}"
        self.option_set_allow_list_ocr:str = text_general.map[f'option_set_allow_list_ocr_{self.current_language}']
        self.option_add_allow_list_ocr:str = text_general.map[f'option_add_allow_list_ocr_{self.current_language}']
        self.option_remove_allow_list_ocr:str = text_general.map[f'option_remove_allow_list_ocr_{self.current_language}']
        self.option_all_allow_list_ocr:str = text_general.map[f'option_all_allow_list_ocr_{self.current_language}']
        #block list ocr
        self.option_menu_block_list_ocr:str = f"{Colors.GREEN}4:{Colors.RESET} {text_general.map[f'option_menu_block_list_ocr_{self.current_language}']}"
        self.option_set_block_list_ocr:str = text_general.map[f'option_set_block_list_ocr_{self.current_language}']
        self.option_add_block_list_ocr:str = text_general.map[f'option_add_block_list_ocr_{self.current_language}']
        self.option_remove_block_list_ocr:str = text_general.map[f'option_remove_block_list_ocr_{self.current_language}']
        self.option_deactivate_block_list_ocr:str = text_general.map[f'option_deactivate_block_list_ocr_{self.current_language}']
        #text_threshold_ocr 
        self.option_menu_set_text_threshold_ocr:str = f"{Colors.GREEN}5:{Colors.RESET} {text_general.map[f'option_menu_set_text_threshold_ocr_{self.current_language}']}"
        self.option_set_text_threshold_ocr:str = text_general.map[f'option_set_text_threshold_ocr_{self.current_language}']
        self.option_default_text_threshold_ocr:str = text_general.map[f'option_default_text_threshold_ocr_{self.current_language}']
        #low_text_ocr
        self.option_menu_set_low_text_ocr:str = f"{Colors.GREEN}6:{Colors.RESET} {text_general.map[f'option_menu_set_low_text_ocr_{self.current_language}']}"
        self.option_set_low_text_ocr:str = text_general.map[f'option_set_low_text_ocr_{self.current_language}']
        self.option_default_low_text_ocr:str = text_general.map[f'option_default_low_text_ocr_{self.current_language}']
        #block list
        self.option_menu_block_list_final:str = f"{Colors.GREEN}7:{Colors.RESET} {text_general.map[f'option_menu_block_list_{self.current_language}']}"
        self.option_set_block_list_final:str = text_general.map[f'option_set_block_list_{self.current_language}']
        self.option_add_block_list_final:str = text_general.map[f'option_add_block_list_{self.current_language}']
        self.option_remove_block_list_final:str = text_general.map[f'option_remove_block_list_{self.current_language}']
        self.option_deactivate_block_list_final:str = text_general.map[f'option_deactivate_block_list_{self.current_language}']
        
        #  type final value
        self.option_menu_select_type_final_value:str = f"{Colors.GREEN}8:{Colors.RESET} {text_general.map[f'option_menu_select_type_final_value_{self.current_language}']}"
        self.option_select_type_final_value:str = text_general.map[f'option_select_type_final_value_{self.current_language}']
        self.option_default_type_final_value:str = text_general.map[f'option_default_type_final_value_{self.current_language}']
        
        self.option_test_setting_area:str =  f"{Colors.YELLOW}9: {text_general.map[f'option_test_setting_area_{self.current_language}']}{Colors.RESET}"
        self.option_menu_area:str =  f"{Colors.BLUE}➔{Colors.RESET} {text_general.map[f'option_menu_area_{self.current_language}']}"
        
        #copy_properties area 
        self.option_copy_from_other_area:str =  f"{Colors.GREEN}10:{Colors.RESET} {text_general.map[f'option_copy_from_other_area_{self.current_language}']}"

        
    @property
    def folder_manager(self) -> FolderManager:
        return self._folder_manager()

    @property
    def setting_manager(self) -> SettingManager: 
        return self._setting_manager()
    
    @property
    def list_areas_model(self) -> list[AreaOcrModel]:
        list_areas = sorted(self.setting_manager.get_areas_model_from_file_setting(), key=lambda model: model.key.value)
        return list_areas

    def handle_options_main_area_setting(self) -> str:
        # HANDLE MAIN AREAS OPTIONS
        others_options=[
                        self.option_menu_set_group_name_area,
                        self.option_menu_allow_list_ocr ,
                        self.option_menu_block_list_ocr,
                        self.option_menu_set_text_threshold_ocr,
                        self.option_menu_set_low_text_ocr,
                        self.option_menu_block_list_final,
                        self.option_menu_select_type_final_value, 
                        self.option_copy_from_other_area,
                            self.option_test_setting_area,
                            self.option_menu_area,
                            self.option_back_to_main_menu
                            ]
        
     
        next_inert_menu = self.prompt_options(default_option=self.option_menu_set_name_area,
                                     others_options=others_options, 
                                    message=text_general.map[f"message_to_continue_{self.current_language}"])
        return next_inert_menu
    
    def handle_group_area(self, area_model:AreaOcrModel, list_areas_model:list[AreaOcrModel], current_option:str ):
        # MARK:HANDLE GROUP AREA
        # name_area ∈ None a∈A
        # name_area ∈/ None group_name a∈/A∩B
        
        list_name_group_with_prefix = [f"{self.name_with_prefix_or_name(name=area_model.group_name.value, prefix_name=area_model.name.value)}" 
                                for area_model in list_areas_model if area_model.group_name.value is not None]
        
        list_name_of_group = [area_model.group_name.value for area_model in list_areas_model if area_model.group_name.value is not None]
        set_name_of_group:set[str] = set(list_name_of_group)
        list_name_of_group = list(set_name_of_group)
        
        #REMOVE CURRENT AREA GROUP OF THE LIST OPTIONS
        if area_model.group_name.value:
            list_name_of_group.remove(area_model.group_name.value)
        
        list_to_group_to_remove:list[str] =[]
        
        # IF THE CURRENT AREA NAME ARE IN ANOTHER GROUP REMOVE FROM THE OPTIONS .    
        for other_group_name  in list_name_of_group:
            if f"{self.name_with_prefix_or_name(name=other_group_name, prefix_name=area_model.name.value)}" in list_name_group_with_prefix:
                list_to_group_to_remove.append(other_group_name) 
        
        for name in list_to_group_to_remove:
            list_name_of_group.remove(name)
        
        if not list_name_of_group or current_option == self.option_create_a_new_group:
            name_group_area:str = self.prompt_string_name_value(ask=text_general.map[f"message_set_group_name_area_{self.current_language}"] ,
                                                    existing_names=[*list_name_of_group, *list_name_group_with_prefix],
                                                    current_name= area_model.group_name.value,
                                                    prefix=self.prefix(area_model.name.value))
            if name_group_area.lower() == "cancel":
                return self.option_main_setting_area
            
            area_model.group_name.set_value(value=name_group_area)
            current_option = self.option_main_setting_area
        else: 
            # MOVE FIRST OPTION TO DEFAULT      
            first_option = list_name_of_group.pop(0)
            others_options = copy.deepcopy(list_name_of_group)
            others_options.append(self.option_create_a_new_group)
            others_options.append(self.option_back_to_menu_area)
            
            current_option = self.prompt_options(
                                            default_option=first_option,
                                            others_options=others_options, 
                                            message=text_general.map[f"message_to_continue_{self.current_language}"])
            
            if current_option == self.option_back_to_menu_area:
                return self.option_main_setting_area
            
            if current_option in list_name_of_group or current_option == first_option:
                area_model.group_name.set_value(value=current_option)
                current_option = self.option_main_setting_area
                
        self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
        return current_option
    
    
    def handle_allow_list_ocr(self, area_model:AreaOcrModel, current_option:str):
        # MARK: HANDLE ALLOW LIST OCR

        if not area_model.ocr_allow_list.value or current_option == self.option_set_allow_list_ocr:
            chars = self.prompt_string_char_value(ask=self.option_menu_allow_list_ocr) 
            area_model.ocr_allow_list.set_value(value=sorted(chars))
            self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
            return self.option_main_setting_area
        else:
            option_menu_allow_list = self.prompt_options(default_option=self.option_add_allow_list_ocr,
                                     others_options=[
                                         self.option_remove_allow_list_ocr,
                                         self.option_set_allow_list_ocr,
                                         self.option_all_allow_list_ocr,
                                         self.option_back_to_menu_area,
                                     ],
                                     message=text_general.map[f"message_to_continue_{self.current_language}"])
            if option_menu_allow_list == self.option_back_to_menu_area:
                return self.option_main_setting_area
            if option_menu_allow_list == self.option_set_allow_list_ocr:
                return self.handle_allow_list_ocr(area_model=area_model, current_option=self.option_set_allow_list_ocr)
            
            if option_menu_allow_list == self.option_add_allow_list_ocr:
                set_to_add = self.prompt_string_char_value(ask=self.option_menu_allow_list_ocr)
                current_set = set(area_model.ocr_allow_list.value)
                combine = current_set | set_to_add
                area_model.ocr_allow_list.set_value(value=sorted(combine))
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
            if option_menu_allow_list == self.option_remove_allow_list_ocr:
                set_to_remove = self.prompt_string_char_value(ask=self.option_remove_allow_list_ocr)
                current_set = set(area_model.ocr_allow_list.value)
                area_model.ocr_allow_list.set_value(value=sorted(current_set - set_to_remove))
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
            if option_menu_allow_list == self.option_all_allow_list_ocr:
                area_model.ocr_allow_list.set_value(value=None)
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
    
    def handle_block_list_ocr(self, area_model: AreaOcrModel, current_option: str):
        # MARK: HANDLE BLOCK LIST OCR

        if not area_model.ocr_block_list.value or current_option == self.option_set_block_list_ocr:
            chars = self.prompt_string_char_value(ask=self.option_menu_block_list_ocr)
            area_model.ocr_block_list.set_value(value=sorted(chars))
            self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
            return self.option_main_setting_area
        else:
            option_menu_block_list = self.prompt_options(
                default_option=self.option_add_block_list_ocr,
                others_options=[
                    self.option_remove_block_list_ocr,
                    self.option_set_block_list_ocr,
                    self.option_deactivate_block_list_ocr,
                    self.option_back_to_menu_area,
                ],
                message=text_general.map[f"message_to_continue_{self.current_language}"]
            )
            if option_menu_block_list == self.option_back_to_menu_area:
                return self.option_main_setting_area
            if option_menu_block_list == self.option_set_block_list_ocr:
                return self.handle_block_list_ocr(area_model=area_model, current_option=self.option_set_block_list_ocr)
            
            if option_menu_block_list == self.option_add_block_list_ocr:
                set_to_add = self.prompt_string_char_value(ask=self.option_menu_block_list_ocr)
                current_set = set(area_model.ocr_block_list.value)
                combine = current_set | set_to_add
                area_model.ocr_block_list.set_value(value=sorted(combine))
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
            if option_menu_block_list == self.option_remove_block_list_ocr:
                set_to_remove = self.prompt_string_char_value(ask=self.option_remove_block_list_ocr)
                current_set = set(area_model.ocr_block_list.value)
                area_model.ocr_block_list.set_value(value=sorted(current_set - set_to_remove))
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
            if option_menu_block_list == self.option_deactivate_block_list_ocr:
                area_model.ocr_block_list.set_value(value=None)
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
    
    def handle_block_list_final(self, area_model: AreaOcrModel, current_option: str):
        # MARK: HANDLE BLOCK LIST FINAL VALUE

        if not area_model.final_block_list.value or current_option == self.option_set_block_list_final:
            chars = self.prompt_string_char_value(ask=self.option_menu_block_list_final)
            area_model.final_block_list.set_value(value=sorted(chars))
            self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
            return self.option_main_setting_area
        else:
            option_menu_block_list_final = self.prompt_options(
                default_option=self.option_add_block_list_final,
                others_options=[
                    self.option_remove_block_list_final,
                    self.option_set_block_list_final,
                    self.option_deactivate_block_list_final,
                    self.option_back_to_menu_area,
                ],
                message=text_general.map[f"message_to_continue_{self.current_language}"]
            )
            if option_menu_block_list_final == self.option_back_to_menu_area:
                return self.option_main_setting_area
            if option_menu_block_list_final == self.option_set_block_list_final:
                return self.handle_block_list_final(area_model=area_model, current_option=self.option_set_block_list_final)
            
            if option_menu_block_list_final == self.option_add_block_list_final:
                set_to_add = self.prompt_string_char_value(ask=self.option_menu_block_list_final)
                current_set = set(area_model.final_block_list.value)
                combine = current_set | set_to_add
                area_model.final_block_list.set_value(value=sorted(combine))
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
            if option_menu_block_list_final == self.option_remove_block_list_final:
                set_to_remove = self.prompt_string_char_value(ask=self.option_remove_block_list_final)
                current_set = set(area_model.final_block_list.value)
                area_model.final_block_list.set_value(value=sorted(current_set - set_to_remove))
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
            if option_menu_block_list_final == self.option_deactivate_block_list_final:
                area_model.final_block_list.set_value(value=None)
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area
    
    def handle_text_threshold_options(self, area_model:AreaOcrModel):
        # MARK: HANDLE TEXT THRESHOLD

        def ask_float_value():
            value_text_threshold = self.prompt_set_float_value(ask=self.option_set_text_threshold_ocr)
            area_model.ocr_text_threshold.set_value(value=value_text_threshold)
            self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
            return self.option_main_setting_area

        if area_model.ocr_text_threshold.value == area_model.ocr_text_threshold.default:
            ask_float_value()
        else:
            inner_option = self.prompt_options(
                default_option=self.option_set_text_threshold_ocr,
                others_options=[
                    self.option_default_text_threshold_ocr,
                    self.option_back_to_menu_area
                ],
                message=text_general.map[f"message_to_continue_{self.current_language}"]
            )

            if inner_option == self.option_back_to_menu_area:
                return self.option_main_setting_area

            if inner_option == self.option_default_text_threshold_ocr:
                # Reset to default threshold value
                area_model.ocr_text_threshold.set_value(value=area_model.ocr_text_threshold.default)
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area

            if inner_option == self.option_set_text_threshold_ocr:
                ask_float_value()
        

        return self.option_main_setting_area

    def handle_low_text_options(self, area_model:AreaOcrModel):
        # MARK: LOW TEXT

        def ask_float_value():
            value_low_text = self.prompt_set_float_value(ask=self.option_set_low_text_ocr)
            area_model.ocr_low_text.set_value(value=value_low_text)
            self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
            return self.option_main_setting_area

        if area_model.ocr_low_text.value == area_model.ocr_low_text.default:
            ask_float_value()
        else:
            inner_option = self.prompt_options(
                default_option=self.option_set_low_text_ocr,
                others_options=[
                    self.option_default_low_text_ocr,
                    self.option_back_to_menu_area
                ],
                message=text_general.map[f"message_to_continue_{self.current_language}"]
            )

            if inner_option == self.option_back_to_menu_area:
                return self.option_main_setting_area

            if inner_option == self.option_default_low_text_ocr:
                # Reset to default low text value
                area_model.ocr_low_text.set_value(value=area_model.ocr_low_text.default)
                self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
                return self.option_main_setting_area

            if inner_option == self.option_set_low_text_ocr:
                ask_float_value()

        return self.option_main_setting_area
    
    
    def loop_area_setting(self, current_area_model:AreaOcrModel,
                        list_areas_model:list[AreaOcrModel], current_option:str = None):
        # MARK: LOOP AREA SETTING 

        if not current_option:
            current_option = self.option_main_setting_area
            
        while True:
                
            if current_option == self.option_main_setting_area:
                current_option = self.handle_main_setting_areas(area_model=current_area_model)
                
            elif current_option == self.option_menu_set_name_area:
                current_option = self.handle_set_name_area(area_model=current_area_model, 
                                                           list_areas_model= list_areas_model)

            elif current_option in {self.option_menu_set_group_name_area, self.option_create_a_new_group}:
                current_option = self.handle_group_area(area_model = current_area_model,
                                                        list_areas_model = list_areas_model,
                                                        current_option = current_option)
                
            elif current_option == self.option_menu_allow_list_ocr:
                current_option = self.handle_allow_list_ocr(area_model = current_area_model,
                                                            current_option = current_option)
                
            elif current_option == self.option_menu_block_list_ocr:
                current_option = self.handle_block_list_ocr(area_model=current_area_model, 
                                                            current_option= current_option)
                
            elif current_option == self.option_menu_set_text_threshold_ocr:
                current_option = self.handle_text_threshold_options(area_model=current_area_model)
                
            elif current_option == self.option_menu_set_low_text_ocr:
                current_option = self.handle_low_text_options(area_model=current_area_model)
                
            elif current_option == self.option_menu_block_list_final:
                current_option = self.handle_block_list_final(area_model= current_area_model,
                                                              current_option= current_option)
                
            elif current_option == self.option_menu_select_type_final_value:
                current_option = self.handle_select_type_final_value(area_model=current_area_model)
                
            elif current_option == self.option_test_setting_area:
                empty_folder = self.panel_test_ocr(area_model=current_area_model)
                
                if empty_folder:
                    current_option = self.option_main_setting_area
                    continue
                else:
                    current_option = self.handle_options_main_area_setting()
                    
            elif current_option == self.option_copy_from_other_area:
                self.handle_copy_properties_area(area_to_update=current_area_model)
                current_option = self.option_main_setting_area
                continue
            
            elif current_option == self.option_menu_area:
                break
            
            elif current_option == self.option_back_to_main_menu:
                return self.option_back_to_main_menu
            
        self.handle_list_area_setting()
        
    def menu_main_setting_areas(self):
        # MARK: MAIN SETTING AREAS
        
        option:str = None
        for area_model in self.list_areas_model:            
            if self.setting_manager.map_areas_state[area_model.key.value]:
                continue
            
            option = self.loop_area_setting(current_area_model=area_model, list_areas_model=self.list_areas_model)
        
            if option == self.option_back_to_main_menu:
                return self.option_show_panel_project
        
        option = self.handle_list_area_setting()
        
        if option == self.option_back_to_main_menu:
            return self.option_show_panel_project
            
        return self.option_show_panel_project

    def handle_main_setting_areas(self, area_model:AreaOcrModel) -> str:
        self.panel_area_model(area_model=area_model, dict_help=text_step_help.help_main_area_menu)
        return self.handle_options_main_area_setting()

    def handle_set_name_area(self, area_model:AreaOcrModel, list_areas_model:list[AreaOcrModel]):
        # MARK: HANDLE SET NAME AREA

        list_name_with_group = [f"{self.name_with_suffix_or_name(name=area_model.name.value, suffix_name=area_model.group_name.value)}" 
                                for area_model in list_areas_model if area_model.name.value is not None]
        
        current_name:str | None = None
        if area_model.name.value:
            current_name = self.name_with_suffix_or_name(name=area_model.name.value, suffix_name=area_model.group_name.value)
            
        name_area = self.prompt_string_name_value(
            ask=text_general.map[f"message_set_name_area_{self.current_language}"],
            existing_names=list_name_with_group,
            current_name=current_name,
            suffix=self.suffix(name=area_model.group_name.value)
        )
        
        if name_area.lower() == "cancel":
            return self.option_main_setting_area

        area_model.name.set_value(value=name_area)
        self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
        return self.option_main_setting_area

    def handle_select_type_final_value(self, area_model:AreaOcrModel):
        # MARK: HANDLE TYPE FINAL VALUE

        type_final_value = self.prompt_options(
            default_option=None,
            others_options=area_model.type_final_value.options,
            message=self.option_select_type_final_value)
        
        area_model.type_final_value.set_value(value=type_final_value)
        self.setting_manager.update_areas_ocr_section_config(area_model=area_model)
        return self.option_main_setting_area
    
    def handle_list_area_setting(self):
        # MARK: HANDLE LIST AREA SETTING
        
        list_menu_str_area_model:list[dict[str, str | AreaOcrModel]] = []
        self.setting_manager.__map_areas_state = None
        
        for area_model in self.list_areas_model:
            if area_model.name.value:
                name_menu_area = f"{self.get_full_name_area(area_model)}{Colors.GREEN} ✔️{Colors.RESET}"
            else:
                name_menu_area =  f"{Colors.RED}{self.get_full_name_area(area_model)}{Colors.RESET}"
            list_menu_str_area_model.append({"name_menu_area":name_menu_area, "area_model": area_model})
        
        areas_name = [value["name_menu_area"] for value in list_menu_str_area_model]
        option = self.prompt_options(default_option=None, others_options=[*areas_name, self.option_back_to_main_menu])
        area_selected:AreaOcrModel = None
        
        if option == self.option_back_to_main_menu:
            return self.option_back_to_main_menu
            
        
        for area_name_key in list_menu_str_area_model:
            if option == area_name_key["name_menu_area"]:
                area_selected =  area_name_key["area_model"]
        
        
        self.loop_area_setting(current_area_model=area_selected, list_areas_model=self.list_areas_model)
        
    def handle_copy_properties_area(self, area_to_update:AreaOcrModel) -> str:
        # MARK: HANDLE COPY AREA PROPERTIES

        add_case_name_without_number = "_1"
        symbol_group_with_space = f"{SET_SYMBOL} "
        area_model_to_copy:AreaOcrModel | None = None
        message_copy_from_other_area:str =  f"{text_general.map[f'message_copy_from_other_area_{self.current_language}']}"

        
        def replace_last_occurrence(s, old, new)->str:
            parts = s.rsplit(old, 1)  
            return new.join(parts)
        
        def contains_number(s) -> bool:
            return bool(re.search(r'\d', s))
        
        def extract_numbers_from_string(s) -> list[int]:
            return [int(num) for num in re.findall(r'\d+', s)]
        
        def check_if_name_is_unique(new_name_area:str, group_name_source:str | None ) -> bool:
            list_area_coincidence = [area for area in self.list_areas_model if area.name.value == new_name_area and area.group_name.value == group_name_source]
            return len(list_area_coincidence) == 0
            
        def get_new_name_area(area_model:AreaOcrModel) -> str:
            name_area_model:str = area_model.name.value
            #case where the name has a number
            if contains_number(name_area_model):
                number_of_name:int = extract_numbers_from_string(name_area_model)[-1]
                is_no_unique_name = True
                
                while is_no_unique_name:
                    new_number:int =  number_of_name + 1
                    new_name_area:str = replace_last_occurrence(name_area_model, str(number_of_name), str(new_number) )
                    number_of_name = new_number  
                    is_no_unique_name = not check_if_name_is_unique(new_name_area, area_model.group_name.value)
                    name_area_model = new_name_area

            else:
                is_no_unique_name = True
                new_name_area = name_area_model + add_case_name_without_number
                while is_no_unique_name:
                    is_no_unique_name = not check_if_name_is_unique(new_name_area, area_model.group_name.value)
                    
                    if is_no_unique_name:
                        number_of_name = extract_numbers_from_string(new_name_area)[-1] + 1
                        new_name_area = replace_last_occurrence(new_name_area, str(number_of_name - 1), str(number_of_name))
                
            
            return new_name_area

            
        def get_area_with_name_and_group(name_area:str, group_name:str|None) -> AreaOcrModel:
            _list_area = [area for area in self.list_areas_model if area.name.value == name_area and area.group_name.value == group_name]
            return _list_area[-1]
            
        
        list_name_areas_without_group:list[str] = [area_model.name.value for area_model in  self.list_areas_model if area_model.name.value is not None and area_model.group_name.value is None]
        list_name_of_group = [f"{symbol_group_with_space}{area_model.group_name.value}" for area_model in self.list_areas_model if area_model.group_name.value is not None]
        set_name_of_group:set[str] = set(list_name_of_group)
        list_name_of_group = list(set_name_of_group)
        selected_option:str =  self.prompt_options(default_option=None,
                                                   others_options=[*list_name_of_group, *list_name_areas_without_group, self.option_menu_area],
                                                   message=message_copy_from_other_area)
        
        if selected_option == self.option_menu_area:
            return self.option_menu_area
        
        if symbol_group_with_space in selected_option:
            group_name = selected_option.replace(symbol_group_with_space, "")
            list_name_areas_with_group:list[str] = [area_model.name.value for area_model in  self.list_areas_model if area_model.name.value is not None and area_model.group_name.value == group_name]
            selected_option:str =  self.prompt_options(default_option=None,
                                                       others_options=[*list_name_areas_with_group, self.option_menu_area], 
                                                       message=message_copy_from_other_area)
            
            if selected_option == self.option_menu_area:
                return self.option_menu_area
            
            area_model_to_copy = get_area_with_name_and_group(name_area=selected_option, group_name=group_name)

        elif symbol_group_with_space not in selected_option:
            area_model_to_copy = get_area_with_name_and_group(name_area=selected_option, group_name=None)
            
        if area_model_to_copy is not None:
            name_of_area_to_update:str = get_new_name_area(area_model=area_model_to_copy) 
            #name
            area_to_update.name.set_value(name_of_area_to_update)
            #group name
            area_to_update.group_name.set_value(value=area_model_to_copy.group_name.value)
            #ocr_allow_list
            area_to_update.ocr_allow_list.set_value(value=area_model_to_copy.ocr_allow_list.value)
            #ocr_block_list
            area_to_update.ocr_block_list.set_value(value=area_model_to_copy.ocr_block_list.value)
            #final_block_list
            area_to_update.final_block_list.set_value(value=area_model_to_copy.final_block_list.value)
            #ocr_text_threshold
            area_to_update.ocr_text_threshold.set_value(value=area_model_to_copy.ocr_text_threshold.value)
            #ocr_low_text
            area_to_update.ocr_low_text.set_value(value=area_model_to_copy.ocr_low_text.value)
            #type_final_value
            area_to_update.type_final_value.set_value(value=area_model_to_copy.type_final_value.value)
            self.setting_manager.update_areas_ocr_section_config(area_model=area_to_update)
    
        return self.option_menu_area
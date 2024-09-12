import os
import re
from types import NoneType
import inquirer
import inquirer.render.console
from rich import print as rprint
from base_class.name_processor import MIDDLE_SYMBOL
from base_class.link_keys import Link
from base_class.shared_keys import SharedKeys
from processor.config_panel import count_lines
from processor.resource_processor import text_general, text_title
from resource_processor.validation import FileValidation
from folder_manager import FolderManager, EnvFolders
from base_class.resolution_dataclass import Resolution
from inquirer.themes import GreenPassion
import custom_event
import custom_prompt
inquirer.render.console.events = custom_event
inquirer.prompt = custom_prompt.prompt
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel


def clear_terminal():
    # Linux
    os.system("clear")
 
class GeneralPrompts:
    
    def __init__(self, **kwargs) -> None:
        
        self.current_language = kwargs.get("current_language", "ES")
        self.available_language = kwargs.get("available_language",  {
                                                                    "English": "EN",
                                                                    "Español": "ES",
                                                                    "Português": "PT"})
        
        self._folder_manager:callable = kwargs.get("folder_manager", None)
        self.console = Console()
        self.main_layout = Layout(ratio=1)
   
    @property
    def folder_manager(self) -> FolderManager | NoneType:
        return self._folder_manager()
    
    def set_link_in_description(self, original_description: str, link: Link, folder_name: str, file_path: str, is_path_folder=False) -> str:
        """Replace a link key with an actual clickable link in the description."""
        
        link_to_click = None
        if file_path:
            link_to_click = self.folder_manager.get_link(file_path, is_path_folder=is_path_folder)
        if link_to_click:
            _link_key = link.create_link_key(type=link, folder_name=folder_name)
            return original_description.replace(f"{_link_key}", f"[blue]{link_to_click}[/blue]")
        return original_description  


    def insert_link(self, original_description: str) -> str:
        
        """Insert the appropriate link into the description based on the link type."""
        
        final_description = original_description  

        def process_link(link_type: Link, is_path_folder: bool = False) -> str:
            folder_name = Link.get_folder_name(type=link_type, text_with_full_link=original_description)
            if folder_name:
                file_path = (
                    self.folder_manager.get_path(folder=EnvFolders.get_by_name(folder_name))
                    if is_path_folder
                    else self.folder_manager.get_the_recent_file_path(folder=EnvFolders.get_by_name(folder_name))
                )
                return self.set_link_in_description(
                    original_description=final_description,  
                    link=link_type,
                    folder_name=folder_name,
                    file_path=file_path,
                    is_path_folder=is_path_folder
                )
            return final_description  

        if Link.LINK_IMAGE_SETTING.value in original_description:
            final_description = process_link(Link.LINK_IMAGE_SETTING)
        
        if Link.LINK_FOLDER.value in original_description:
            final_description = process_link(Link.LINK_FOLDER, is_path_folder=True)
        
        if Link.LINK_FILE_SETTING.value in original_description:
            final_description = process_link(Link.LINK_FILE_SETTING)
        
        if Link.LINK_VIDEO.value in original_description:
            final_description = process_link(Link.LINK_VIDEO)

        return final_description  

    
    def prompt_string_name_value(self, ask:str, existing_names:list[str],
                                   current_name:str= None,
                                   prefix:str=None,
                                   suffix:str=None,
                                   return_with_suffix:bool = False
                                   ) -> str:
        # MARK:  MENU ASK NAMES

        def name_validation(answers, current: str):
            name_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
            current = re.sub(r'\s+', ' ', current).strip()
            current = current.replace(" ", "_")
            if current.lower() == "cancel":
                return True
                
            if not re.match(name_pattern, current):
                raise inquirer.errors.ValidationError(
                    "", reason=f"Invalid name: {current}. Only letters, numbers, underscores, and hyphens are allowed.")
            
            if current_name == current and not isinstance(current_name, NoneType) :
                return True
            
            if prefix:
                current = f"{prefix}{current}"
            
            if suffix:
                current = f"{current}{suffix}"
                
            if current in existing_names:
                reason = f"The name '{current}' is already in use. Please choose a different name."
                if current:
                    if MIDDLE_SYMBOL in current: 
                        reason = f"{current}, is already in use. Please choose a different name"
                else:
                    reason = f"The name '{current}' is already in use. Please choose a different name."
                    
                raise inquirer.errors.ValidationError(" ", reason= reason)
            
            return True
        
        question = [inquirer.Text("ask_string", message=ask, validate=name_validation)]
        answers = inquirer.prompt(question, theme=GreenPassion(), raise_keyboard_interrupt= True)
        answers["ask_string"] = re.sub(r'\s+', ' ', answers["ask_string"]).strip()
        answers["ask_string"] = answers["ask_string"].replace(" ", "_")
        if suffix and return_with_suffix:
            return f"{answers['ask_string']}{suffix}"
        return answers["ask_string"]

    def prompt_string_char_value(self, ask:str) -> set[str]:
        question = [inquirer.Text("ask_string_char", message=ask)]
        answers = inquirer.prompt(question, theme=GreenPassion(), raise_keyboard_interrupt= True)
        return_value = set(answers["ask_string_char"])
        return return_value
    
        
    def prompt_set_float_value(self,  ask:str, min:float = 0, max:float =1) -> float:      
        def number_validation(answers, current):
            try:
                number = float(current)
            except ValueError:
                raise inquirer.errors.ValidationError("", reason="Input must be a number.")
            
            if number < min or number > max:
                raise inquirer.errors.ValidationError("", reason=f"Number must be between {min} and {max}.")
            return True
        
        question = [inquirer.Text("ask_number", message=ask, validate=number_validation)]
        answers = inquirer.prompt(question, theme=GreenPassion(), raise_keyboard_interrupt= True)
        return round(float(answers["ask_number"]), 2)

    def prompt_options(self, default_option:str, others_options:list[str]=[], message:str ="") -> str:
        # MARK:  LIST SIMPLE OPTIONS 

        if default_option:
            choices =  [default_option, *others_options]
        else:
            choices = others_options
        questions = [
            inquirer.List(
                "simple_menu_options",
                default= default_option,
                message = message,
                carousel= True,
                choices= choices ,
            ),
        ]
        answers = inquirer.prompt(questions, theme=GreenPassion(), raise_keyboard_interrupt= True)
        if not answers:
            answers = {}
        return answers.get("simple_menu_options", None)
    

    def prompt_options_file(self, 
              dict_text_help:dict,
              message:str,
              option_to_validate:str,
              others_options:list[str],
              folder:EnvFolders,
              max_image_resolution:Resolution=None,
              extension_str:str= ".png",
              list_remove_i_after_validate:list[str] = None,
              key_item:str= None,
              )-> str :
        
        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")
        print("")
        total_lines_description = 0 
        title_and_description:int = int((len(dict_text_help.keys())/len(self.available_language.keys()))/2)
        for step in range(0, title_and_description):

            title_key = f"step_{step}_title_{self.current_language}"
            description_key = f"step_{step}_description_{self.current_language}"
            title = f"[green]{step+1}: {dict_text_help[title_key]}[/green]"
            description = dict_text_help[description_key]
            description = self.insert_link(original_description=description)
            panel_link = Panel(description, title=title, style="white", title_align="left")
            lines = count_lines(content=panel_link, content_type="panel", panel_width=self.console.width)
            total_lines_description += lines
            self.main_layout.add_split(Layout(panel_link, name=f"{step}_description", ratio=lines))


        self.console.print(self.main_layout, height=total_lines_description)
        self.main_layout = Layout()
        
        if option_to_validate:
            choices= [option_to_validate,*others_options]
        else:
            choices= others_options
        
        questions = [inquirer.List(
                        "menu_file",
                        message= message,
                        choices= choices,
                        validate = FileValidation(folder_manager=self.folder_manager,
                                                  folder=folder,
                                                  list_options_to_ignore=others_options,
                                                  extension_str=extension_str,
                                                  max_image_resolution=max_image_resolution).validation_file)]
        
        answers = inquirer.prompt(questions, theme=GreenPassion(), raise_keyboard_interrupt= True)
        
        if answers["menu_file"] == option_to_validate and \
                                list_remove_i_after_validate and \
                                key_item in list_remove_i_after_validate:
            
            list_remove_i_after_validate.remove(key_item) 
            
        return answers["menu_file"]



    def prompt_checks(self,
                      dict_set_checks: dict[str,list],
                      dict_set_defaults:dict[str,list] = [],
                      common_checks:list =[],
                      default_check_str:str = None,
                      next_option:str =None,
                      back_option:str = None,
                      cancel_option:str = None,
                      message:str = "",
                      clear_screen_each_set:bool =True) -> dict[str,list] | None:
        
        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")
        print("")
        selected_vars:dict[str,list] = {}
        for _set, cols in dict_set_checks.items():
            default:list = dict_set_defaults[_set] or []
            if common_checks:
                 cols.extend(common_checks)
            if default_check_str:
                default = [default_check_str, *default]
                cols = [default_check_str, *cols]
                
            questions = [
                inquirer.Checkbox(
                    f'include_{_set}',
                    message=f'{message} {_set}',
                    choices=cols,
                    carousel=True,
                    default=default,
                )]
            if back_option and next_option and cancel_option:
                questions.append(inquirer.List(f'next_back_cancel_{_set}', choices= [next_option, back_option, cancel_option]))

            answers = inquirer.prompt(questions, theme= GreenPassion())
            selected_vars[_set] = answers[f'include_{_set}']
            next_back_cancel = answers[f'next_back_cancel_{_set}']
            
            if next_back_cancel == cancel_option:
                return None
            if next_back_cancel == back_option:
                self.prompt_checks(dict_set_checks, dict_set_defaults,common_checks, default_check_str, 
                                   next_option, back_option, cancel_option, message)
            
            if default_check_str in selected_vars[_set]:
                selected_vars[_set].remove(default_check_str)
            
            if clear_screen_each_set:
                clear_terminal()
                rprint(f"[green]{text_title.title}[green]")
                rprint(f"")
                
        return selected_vars
        

if __name__ == "__main__":
    """
    
 d888888b d88888b .d8888. d888888b   d8888b. d8888b.  .d88b.  .88b  d88. d8888b. d888888b .d8888.
 `~~88~~' 88'     88'  YP `~~88~~'   88  `8D 88  `8D .8P  Y8. 88'YbdP`88 88  `8D `~~88~~' 88'  YP
    88    88ooooo `8bo.      88      88oodD' 88oobY' 88    88 88  88  88 88oodD'    88    `8bo.  
    88    88~~~~~   `Y8b.    88      88~~~   88`8b   88    88 88  88  88 88~~~      88      `Y8b.
    88    88.     db   8D    88      88      88 `88. `8b  d8' 88  88  88 88         88    db   8D
    YP    Y88888P `8888Y'    YP      88      88   YD  `Y88P'  YP  YP  YP 88         YP    `8888Y'
    """
    self =  GeneralPrompts()
     

    message_checks_set_1 = text_general.map[f"message_checks_set_1_{self.current_language}"] 
    message_checks_set_2 = text_general.map[f"message_checks_set_2_{self.current_language}"]
    message_use_keys =text_general.map[f"message_use_keys_{self.current_language}"] 
    #SET CHECKS 1
    lang_timestamp_seconds =  text_general.map[f"timestamp_seconds_{self.current_language}"]
    lang_session_code = text_general.map[f"session_code_{self.current_language}"]
    lang_is_start_session =  text_general.map[f"is_start_session_{self.current_language}"]
    lang_is_end_session = text_general.map[f"is_end_session_{self.current_language}"]
    lang_is_change_detected =  text_general.map[f"is_change_detected_{self.current_language}"]
    lang_session_captures_number = text_general.map[f"session_captures_number_{self.current_language}"]
    lang_date =  text_general.map[f"date_{self.current_language}"]
    session_code = SharedKeys.KEY_SESSION_CODE.value  # 'session_code'
    is_start_session = SharedKeys.KEY_IS_START_SESSION.value  # 'is_start_session'
    is_end_session = SharedKeys.KEY_IS_END_SESSION.value  # 'is_end_session'
    is_change_detected = SharedKeys.KEY_IS_CHANGE_DETECTED.value  # 'is_change_detected'
    timestamp_seconds = SharedKeys.KEY_TIMESTAMP_SECONDS.value  # 'timestamp_seconds'
    session_captures_number = SharedKeys.KEY_SESSION_CAPTURES_NUMBER.value  # 'session_captures_number'
    date = SharedKeys.KEY_DATE.value  # 'date'
    #SET CHECKS 2
    lang_area_key_number = text_general.map[f"area_key_number_{self.current_language}"]
    lang_area_key_raw_value =  text_general.map[f"area_key_raw_value_{self.current_language}"]
    lang_area_key_path_image =  text_general.map[f"area_key_path_image_{self.current_language}"]
    area_key_number = SharedKeys.KEY_AREA_NUMBER.value # in tx×
    area_key_raw_value = SharedKeys.KEY_AREA_RAW_VALUE.value # in tx×
    area_key_path_image = SharedKeys.KEY_AREA_PATH_IMAGE.value # in tx×
    #OTHERS OPTIONS
    option_default = text_general.map[f"option_default_{self.current_language}"]
    option_next = text_general.map[f"option_next_{self.current_language}"]
    option_back = text_general.map[f"option_back_{self.current_language}"]
    option_cancel = text_general.map[f"option_cancel_{self.current_language}"]

    
    map_dict_vars = {lang_timestamp_seconds:timestamp_seconds ,
                    lang_session_code:session_code,
                    lang_is_start_session:is_start_session,
                    lang_is_end_session:is_end_session,
                    lang_is_change_detected:is_change_detected,
                    lang_session_captures_number:session_captures_number,
                    lang_date:date,
                    lang_area_key_number:area_key_number,
                    lang_area_key_path_image:area_key_path_image,
                    lang_area_key_path_image:area_key_raw_value}
    
    map_dict_sets = {message_checks_set_1:"KEYS_TO_UNPACK_IN_TX" ,
                    message_checks_set_2:"TX_THIRD_INDEX_DIMENSION",
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
        
        
        
    
    dict_defaults = {message_checks_set_1:[lang_timestamp_seconds],
                     
                     message_checks_set_2: [lang_area_key_number]}
    
    dict_columns = {message_checks_set_1: [  lang_timestamp_seconds,
                                                lang_session_code,
                                                lang_is_start_session,
                                                lang_is_end_session,
                                                lang_is_change_detected,
                                                lang_session_captures_number,
                                                lang_date],
                    
                    message_checks_set_2: [     lang_area_key_number,
                                                lang_area_key_raw_value,
                                                lang_area_key_path_image]}
    
    
    
    prompt_check = self.prompt_checks(dict_set_checks=dict_columns,
                                                dict_set_defaults=dict_defaults,
                                                message= message_use_keys,
                                                default_check_str=option_default,
                                                back_option=option_back,
                                                cancel_option=option_cancel,
                                                next_option=option_next)
    
    if not prompt_check:
        print("Cancel")
    else:
        dict_r = translation_options_to_var(dict_result=prompt_check)
        print(dict_r)
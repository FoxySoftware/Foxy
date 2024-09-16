import os
import re
from types import NoneType
import inquirer
import inquirer.render.console
from rich import print as rprint
from base_class.link_keys import Link
from resource_collector import text_general, text_title
from resource_collector.validation import FileValidation
from folder_manager import FolderManager, EnvFolders
from base_class.resolution_dataclass import Resolution
from resource_collector.count_lines_console import count_lines
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
 
MIDDLE_SYMBOL = "_"
class GeneralPrompts:
    
    def __init__(self, **kwargs) -> None:
        
        self.current_language = kwargs.get("current_language", "EN")
        self.available_language = kwargs.get("available_language",  {
                                                                    "English": "EN",
                                                                    "Español": "ES",
                                                                    "Português": "PT"})
        
        self._folder_manager:callable = kwargs.get("folder_manager", None)
        self.console = Console()
        self.main_layout = Layout(ratio=1)
        self.option_select_language:str =  text_general.map[f'option_select_language_{self.current_language}']

    
    @property
    def folder_manager(self) -> FolderManager | NoneType:
        return self._folder_manager()
    
    
    def prompt_resolution(self, dict_text_help:dict[str, str], others_options:list[str] = [] )-> Resolution:
           
        
        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")
        #show help text
        title_and_description:int = int((len(dict_text_help.keys())/len(self.available_language.keys()))/2) 
        for step in range(0,title_and_description):
            title_key = f"step_{step}_title_{self.current_language}"
            description_key = f"step_{step}_description_{self.current_language}"
            rprint(f"[green]{step+1}: {dict_text_help[title_key]}[/green]")
            description = dict_text_help[description_key]
            rprint(f"[white]{description}[/white]\n")
        
        #get the resolution screen    
        option_1:str = Resolution.FOUR_K.string_value
        option_2:str = Resolution.FULL_HD.string_value
        option_3:str = Resolution.TWO_K.string_value
        option_4:str = Resolution.FIVE_K.string_value
        all_options = [option_2, option_3, option_4, * others_options]
        next_option = self.prompt_options(default_option=option_1,
                                            others_options=all_options,
                                            message=text_general.map[f"question_resolution_{self.current_language}"] )
        if next_option in others_options:
            return next_option
        else:
            screen_resolution = Resolution.from_string(next_option)
    
        return screen_resolution
    
    def prompt_seconds_video(self):
        
        def validation_function(answers, current):
            try:
                value = int(current)
            except ValueError:
                raise inquirer.errors.ValidationError('', reason=text_general.map[f"message_integer_value_{self.current_language}"])
            # Check if the value is within the allowed range (1 to 1800 seconds)
            if value < 1 or value > 1800:
                raise inquirer.errors.ValidationError('', reason=text_general.map[f"value_seconds_video_{self.current_language}"])
            return True   
        
        # get second of video screen record
        questions = [ inquirer.Text("seconds_video",
                      message=text_general.map[f"question_seconds_video_{self.current_language}"] ,
                      validate=validation_function),]
        answers = inquirer.prompt(questions, theme=GreenPassion(), raise_keyboard_interrupt=True)
        video_seconds_recording = int(answers["seconds_video"])
        return video_seconds_recording
    
    
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
    
    
    def prompt_welcome(self ,new_project:str, select_project:str, list_projects:list[str] | None)-> str:
        # MARK: OLD MENU WELCOME - require refactor !
        clear_terminal()
        rprint(f"[green]{text_title.title}[green]")

        options = [self.option_select_language, new_project, select_project]
        
        if list_projects is None or len(list_projects) == 0:
            options.remove(select_project)
        
        questions = [
            inquirer.List(
                "start",
                message="Start 🏁",
                choices=options,
                carousel=True,
                
            )]
        answers = inquirer.prompt(questions, theme=GreenPassion(),raise_keyboard_interrupt=True)
        return answers["start"]
    
    def prompt_ask_float_value(self, ask:str,  title:str = None, help:str = None, minimum = 1, limit = 100, main_title= True, round_value=True) -> float:
        # MARK: OLD MENU ASK FLOAT VALUE 
        if main_title:
            clear_terminal()
            rprint(f"[green]{text_title.title}[green]")
        
        if title and help:
            rprint(f"[green]{title}[/green]")
            rprint(f"[white]{help}[/white]\n")
            
        def number_validation(answers, current):
            try:
                number = float(current)
            except ValueError:
                raise inquirer.errors.ValidationError("", reason="Input must be a number.")
            
            if number < minimum or number > limit:
                raise inquirer.errors.ValidationError("", reason=f"Number must be between {minimum} and {limit}.")
            return True
        
        question = [inquirer.Text("ask_number", message=ask, validate=number_validation)]
        answers = inquirer.prompt(question, theme=GreenPassion())
        if round_value:
            return round(float(answers["ask_number"]), 2)
        else:
            return(answers["ask_number"])
    
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
            
            if current_name == current and current_name is not None :
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
                raise inquirer.errors.ValidationError("", reason= reason)
            
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
    
    def prompt_string_url(self, ask:str) -> set[str]:
        
        def url_validation(answers, current:str):
            url_pattern = re.compile(
                r'^(?:http)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ipv4
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            

            if not re.match(url_pattern, current.strip()):
                raise inquirer.errors.ValidationError("", reason=f"Invalid URL :{current.strip()}")
            return True
        
        question = [ (inquirer.Text(name='web_page',
                                         message=ask, validate = url_validation))]
        
        answers = inquirer.prompt(question, theme=GreenPassion(), raise_keyboard_interrupt= True)
        return_value = answers["web_page"].strip()       
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
    pass
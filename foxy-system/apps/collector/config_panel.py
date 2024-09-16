import ast
import threading
import time
import os
import inquirer.render.console
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from inquirer.themes import GreenPassion
from resource_collector import text_panel, text_title
from resource_collector.count_lines_console import count_lines
import custom_event 
import custom_prompt as custom_prompt

inquirer.render.console.events = custom_event
inquirer.prompt = custom_prompt.prompt

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    GRAY = '\033[90m'  
    RESET = '\033[0m'


def clear_terminal():
   os.system("clear")
        

class ConfigProjectPanel():
    
    def __init__(self, **kwargs) -> None:
        self.current_language:str = kwargs.get("current_language", "EN")
        self.dict_options_menu:dict[str,str] = kwargs["dict_options_menu"]
        self.stop_event:threading.Event = kwargs.get("stop_event",  threading.Event())
        self.pause_event:threading.Event = kwargs.get("pause_event",  threading.Event()) 
        self.resume_event:threading.Event = kwargs.get("resume_event",  threading.Event()) 
        self.auto_updatable_section:str = kwargs.get("auto_updatable_section", None) # the section in config.ini
        self.wakeup_signals:callable | None = kwargs.get("wakeup_signals", None)

        self.first_options_blue:int = 3 
        self.last_main_options:int = 1  
        self.last_options_gray:int = 2
        
        self.main_layout:Layout = None
        self.all_options:list[str] = [] # DEFAULT COLOR GREEN | REPRESENT A NOT REQUIRED STEP/OPTION
        self.blue_options:list[str] = [] # GENERAL OPTIONS  
        self.red_options:list[str] = [] # REPRESENT A REQUIRED STEP
        self.grey_options:list[str] = [] # ONLY WHEN A REQUIRED OPTION IS PRESENT | REPRESENT A DEACTIVATE OPTION
        self.yellow_options:list[str] = [] # MAIN OPTION ONLY WHEN IS ACTIVE
        self.menu_dependency:dict[str,str] = {} # IN THE CASE WHERE THE MENU OPTION REQUIRE A SPECIFIC SECTION AND ALL GREEN
        self.last_data_update:dict = None
        self.console = Console()
        self.height_console = 0
        self.width_windows_console = self.console.width
        self.height_windows_console = self.console.height
        self.ratio_update_panel:int = 0
    

    def update_length_console(self, content, content_type:str = "panel", extra_lines:int = 0 ) -> int:
        lines_panel_padding:int = 0
        lines:int = 0
        if content:
            lines = count_lines(content=content, content_type=content_type, panel_width=self.width_windows_console)
        ratio = lines + lines_panel_padding + extra_lines
        self.height_console += ratio
        self.console.height = self.height_console
        return ratio
    
    def console_to_fullscreen(self):
        if self.console.height < self.height_windows_console:
            self.console.height = self.height_windows_console
        
    def set_style_option(self, key:str, number) -> str:
            white_space = "  "
            opt_n = number +1
            
            if opt_n >= 10:
                white_space = " " 
                
            if key in self.red_options:
                return f"{opt_n}:{white_space}{Colors.RED}{text_panel.dict_menu_panel[key]}{Colors.RESET}"
            if key in self.blue_options:
                return f"{opt_n}:{white_space}{Colors.BLUE}{text_panel.dict_menu_panel[key]}{Colors.RESET}"
            if key in self.grey_options:
                return f"{opt_n}:{white_space}{Colors.GRAY}{text_panel.dict_menu_panel[key]}{Colors.RESET}"
            if key in self.yellow_options:
                return f"{opt_n}:{white_space}{Colors.YELLOW}{text_panel.dict_menu_panel[key]}{Colors.RESET}"
           
            return f"{opt_n}:{white_space}{Colors.GREEN}{text_panel.dict_menu_panel[key]}  ✔️{Colors.RESET}"
            
    def show_options(self, options:list[str]) -> str:

        options_text_list = [self.set_style_option(key, number) for number, key in enumerate(options) ]

        def option_validation(answers, current):
            try:
                index = options_text_list.index(current)
                if options[index] in self.grey_options and not options[index] in self.menu_dependency:
                    raise RedOptionException
                
                if options[index] in self.menu_dependency:
                    section_key_lang = self.menu_dependency[options[index]]
                    raise WhiteOptionException
                    
            except RedOptionException:
                raise inquirer.errors.ValidationError("", reason=f"Option {index + 1} not available, complete the required steps.")
            
            except WhiteOptionException :
                raise inquirer.errors.ValidationError("", reason=f"Option {index + 1}  not available, see the section {text_panel.dict_panel_title[section_key_lang]}")
           
            return True
        
        questions = [
            inquirer.List(
                "main_menu",
                message = "",
                carousel= True,
                choices= options_text_list ,
                validate=option_validation
            ),
        ]
        answers = inquirer.prompt(questions, theme=GreenPassion(), raise_keyboard_interrupt=True)
        index = options_text_list.index(answers["main_menu"])
        return options[index]

        
    def show_panel(self, config_data: dict, columns: int = 2) -> str:
        """
        Return the selected option 
        """
        # MARK: CONFIG PANEL
        clear_terminal()
        self.console.clear()
        self.height_console = 0
        self.main_layout = Layout()
        self.red_options = []
        
        panel = Panel(f"[green]{text_title.title}[green]", padding=(1, 2))
        ratio = self.update_length_console(content=panel, extra_lines=1)
        self.main_layout.add_split(Layout(name="header", ratio=ratio))
        self.main_layout["header"].update(panel)
        section_list = list(config_data.items())
        rows = [section_list[i:i + columns] for i in range(0, len(section_list), columns)]
        list_row_layouts:list[Layout] = []
        jump:bool = False
        
        total_ratio = 0
        dict_rows_ratio = {}
        layout_auto_update:Layout = None
        panel_auto_update:Layout = None
        
        for n_row, row in enumerate(rows):
            panels = []
            for section, settings in row:
                table = self.create_table_from_section(section, settings)
                panel = Panel(table,
                              title=text_panel.dict_panel_title[f'{section}_{self.current_language}'],
                              title_align="center",
                              expand=True, 
                              padding=(1, 2),
                              highlight=True) 
                
                if self.auto_updatable_section and section == self.auto_updatable_section:
                    ratio = self.update_length_console(content=panel)
                    self.main_layout.add_split()
                    layout_auto_update = Layout(name="auto_updatable", ratio=ratio)
                    panel_auto_update = panel
                    jump = True
                    continue
                else:
                    panels.append(panel)
                    lines_panel = count_lines(content=panel, panel_width=(self.width_windows_console//2),)
                    if dict_rows_ratio.get(n_row, None):
                        if lines_panel > dict_rows_ratio[n_row]:
                            dict_rows_ratio[n_row] = lines_panel+1
                    else:
                        dict_rows_ratio[n_row] = lines_panel +1
                        
            if jump:
                jump = False
                continue
            row_layout = Layout()
            row_layout.split_row(*[Layout(panel, name=f'{section}_{self.current_language}' ) for panel in panels])
            list_row_layouts.append(row_layout)
        
        total_ratio = 0
        for lines_rows_panel in dict_rows_ratio.values():
            
            total_ratio+= lines_rows_panel
        
        self.update_length_console(content=None, extra_lines=total_ratio)
        self.main_layout.add_split(Layout(name="content", ratio=total_ratio))
        self.main_layout['content'].split_column(*list_row_layouts)
        
        # add layout to the end. 
        if layout_auto_update and panel_auto_update:
            layout_auto_update.update(panel_auto_update)
            self.main_layout.add_split(layout_auto_update)
        
        self.console.print(self.main_layout)
        self._set_colors_list()
        selected_option = self.show_options(self.all_options)
        return self.dict_options_menu[selected_option]
    
    def _set_colors_list(self):
        
        self.all_options = [key for key in self.dict_options_menu.keys()]
        self.blue_options = self.all_options[:self.first_options_blue]
        
        if len(self.red_options) != 0:
            self.grey_options = self.all_options[-self.last_options_gray:]
            self.yellow_options = []
        else :
            self.grey_options = []
            self.yellow_options = self.all_options[-self.last_main_options:]
            
        if self.menu_dependency:
            for key in self.menu_dependency.keys():
                self.grey_options.append(key)

    def _get_and_set_dependent_menu(self, section:str, settings:dict[str, str]) -> list[str]:
        _dependent_list_str:str = settings.pop("_dependent_list", "[]")
        _dependent_list:list[str] = ast.literal_eval(_dependent_list_str)
        
        for dependent_menu_key in _dependent_list:
            menu_key_lang =  f"{dependent_menu_key}_{self.current_language}" 
            section_lang = f"{section}_{self.current_language}"
            self.menu_dependency = {menu_key_lang:section_lang}
        
        return _dependent_list
    
    def is_required_option(self, section:str, settings:dict[str, str]) -> bool:
        if "True" == settings.get("required", "False"):
            self.red_options.append(f"{section}_{self.current_language}")
            return True
        return False
    
    def create_table_from_section(self,section:str, settings: dict) -> Table:
        
        def format_key(s):
            if not s:  
                return s
            key = s[0].upper() + s[1:]
            return key.replace("_", " ")

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="bold cyan",)
        style_value_color = "bold green"
        is_required:bool = self.is_required_option(section=section, settings=settings)
        if is_required:
            style_value_color = "bold red"

        has_dependent:list[str] = self._get_and_set_dependent_menu(section=section, settings=settings)
        if has_dependent:
            style_value_color = "bold white"
 
        table.add_column("Value", style=style_value_color, no_wrap=False)

        for key, value in settings.items():
            table.add_row(format_key(key), value)

        return table
    
    def update_automatic_layout(self, function_return_dict:callable, seconds_period:int = 1):
        clear_terminal()
        panel_state = Panel(Text(text="Ctrl + C to Stop | Ctrl + Z to Pause"), title= "RUNNING", border_style="bold green")
        panel_task:Panel = Panel("", title="", border_style="bold white")
        
        ratio = self.update_length_console(content=panel_state)
        self.main_layout.add_split(Layout(name="state", ratio=ratio))
        self.main_layout["state"].update(panel_state)
        self.console.print(self.main_layout)
        if self.auto_updatable_section:
            white_style = "bold white"
            yellow_style = "bold yellow"
            current_style = yellow_style
            while not self.stop_event.is_set():
                title:str= text_panel.dict_panel_title[f'{self.auto_updatable_section}_{self.current_language}']

                if self.pause_event.is_set():
                    title = "PAUSED"
                    panel_state = Panel( 
                        Text(text="Ctrl + Z to Resume", style="bold yellow"),title= "PAUSED", border_style="bold yellow")
                    self.main_layout["state"].update(panel_state)
                else:
                    panel_state = Panel(Text(text="Ctrl + C to Stop | Ctrl + Z to Pause"), title= "RUNNING", border_style="bold green")
                    self.main_layout["state"].update(panel_state)
                    
                self.last_data_update = function_return_dict()
                if not self.last_data_update:
                    time.sleep(seconds_period)
                    continue
                current_time = f"UTC {time.strftime('%H:%M:%S')}"
                self.last_data_update["updated_at"] = current_time
                    
                table = self.create_table_from_section(section=self.auto_updatable_section, settings=self.last_data_update)
                panel_task:Panel = Panel(table, title=title, border_style=current_style)
                if current_style == yellow_style:
                    current_style = white_style
                else:
                    current_style = yellow_style
                try:
                    self.main_layout["auto_updatable"].update(panel_task)
                    self.console_to_fullscreen()

                except:
                    ratio = self.update_length_console(content=panel_task)
                    self.console_to_fullscreen()
                    self.main_layout.add_split(Layout(name="auto_updatable", ratio=ratio))
                    self.main_layout["auto_updatable"].update(panel_task)
                      
                self.console.print(self.main_layout)
                time.sleep(seconds_period)
                
                
            self.last_data_update = function_return_dict()
            table = self.create_table_from_section(section=self.auto_updatable_section, settings=self.last_data_update)
            title:str= text_panel.dict_panel_title[f'{self.auto_updatable_section}_{self.current_language}']
            panel_task:Panel = Panel(table, title=title, border_style=current_style)
            panel_state = Panel(Text(text=""), title= "STOPPED", border_style="bold red")
            self.main_layout["state"].update(panel_state)
            self.main_layout["auto_updatable"].update(panel_task)
            clear_terminal()
            self.console.print(self.main_layout)
         

class RedOptionException(Exception):
    """Base class for custom exceptions."""
    def __init__(self, message=""):
        super().__init__(message)  

    def __str__(self):
        return f"{self.args[0]} "

class WhiteOptionException(Exception):
    """Base class for custom exceptions."""
    def __init__(self, message=""):
        super().__init__(message)  

    def __str__(self):
        return f"{self.args[0]} "
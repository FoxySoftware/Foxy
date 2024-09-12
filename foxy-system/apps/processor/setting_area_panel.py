import os
import platform
from io import StringIO
from types import NoneType
from rich.console import Console
from rich.table import Table, box
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from folder_manager import FolderManager, EnvFolders
from resource_processor import  text_title
from base_class.link_keys import Link
from base_class.table_models import (ColumnTableSetting, 
                                            ItemTableSetting,
                                            RowTableSetting,
                                            TableSetting)



def clear_terminal():
    os.system("clear")


class SettingAreaPanel():
    
    def __init__(self, **kwargs) -> None:
        self.current_language:str = kwargs.get("current_language", "EN")
        self.available_language:dict[str, str] = kwargs.get("available_language",{"English": "EN"})
        self.folder_manager:FolderManager = kwargs.get("folder_manager", None)
        self.main_layout = Layout()
        self.console = Console()
        self.height_console = 0
        self.width_windows_console = self.console.width
        self.height_windows_console = self.console.height
        self.dict_panel_table_data = {}
        self.keywords_links = [Link.LINK_FOLDER, Link.LINK_IMAGE_SETTING, Link.LINK_FILE_SETTING]
        self.help_links:list[dict[str,str]] = [] 
    
    @staticmethod
    def count_lines(content, panel_width, content_type='panel'):
        panel_width  = panel_width
        buffer = StringIO()
        console = Console(file=buffer, width=panel_width)
        if content_type == 'text':
            content = Text.from_markup(content)
        console.print(content)
        content_output = buffer.getvalue()
        lines = content_output.splitlines()
        lines = [line for line in lines if line.strip()]
        return len(lines)


    def update_length_console(self, content, content_type:str = "panel", extra_lines:int = 0 ) -> int:
        lines_panel_padding:int = 0
        lines:int = 0
        if content:
            lines = self.count_lines(content=content, content_type=content_type, panel_width=self.width_windows_console)
        ratio = lines + lines_panel_padding + extra_lines
        self.height_console += ratio
        self.console.height = self.height_console
        return ratio
    
    def create_title(self, title:str = text_title.title):
        if self.width_windows_console < 120:
            title = text_title.logo
        panel = Panel(f"[green]{title}[green]")
        ratio = self.update_length_console(content=panel, extra_lines=1)
        self.main_layout.add_split(Layout(name="header", ratio=ratio))
        self.main_layout["header"].update(panel)
         
    
    def show_panel(self,
                   panel_name = "panel_1",
                   data_items:dict = None,
                   dict_help:dict[str,str] = None,
                   table_setting:TableSetting = TableSetting.default(),
                   items_setting:ItemTableSetting = [ItemTableSetting.default()]) -> None:
        self.main_layout = Layout()
        self.height_console = 0
        
        clear_terminal()
        self.create_title()

        if dict_help:
            self.create_help_panel(dict_text_help=dict_help)
       
        if data_items :
            self.dict_panel_table_data[panel_name] = {"data_items":data_items,
                                                      "dict_help":dict_help,
                                                      "table_setting":table_setting,
                                                      "items_setting":items_setting } 
            
            self.create_table(data_items=data_items, items_setting=items_setting, table_setting=table_setting, panel_name=panel_name)
            
        self.console.print(self.main_layout)
    
    def add_panel(self,
                  panel_name:str= "new_panel",
                  data_items:dict = None,
                  dict_help:dict[str,str] = None,
                  table_setting:TableSetting = TableSetting.default(),
                  items_setting:ItemTableSetting = [ItemTableSetting.default()],
                  position_help:str="bottom") -> None:
        
        clear_terminal()
        self.main_layout = Layout()
        self.height_console = 0
       
        self.create_title()
        for key, value in self.dict_panel_table_data.items():
            if value["dict_help"]:
                self.create_help_panel(dict_text_help=value["dict_help"])
            self.create_table(data_items=value["data_items"], items_setting=value["items_setting"], table_setting=value["table_setting"], panel_name=key)
        
        if dict_help and position_help == "top":
            self.create_help_panel(dict_text_help=dict_help, panel_name=f"help_{panel_name}")
            
        if data_items :
            self.create_table(data_items=data_items, items_setting=items_setting, table_setting=table_setting, panel_name=panel_name)
        
        if dict_help and position_help == "bottom":
            self.create_help_panel(dict_text_help=dict_help, panel_name=f"help_{panel_name}")
            
        self.console.print(self.main_layout)
    
    def extract_link(self, title, description: str) -> str:
        
        link:str = None
        if Link.LINK_IMAGE_SETTING.value in description:
            folder_name = Link.get_folder_name(type=Link.LINK_IMAGE_SETTING, text_with_full_link=description)
            file_path = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.get_by_name(folder_name), only_extension=".png")
            if file_path:
                link = self.folder_manager.get_link(file_path)
        elif Link.LINK_FOLDER.value in description:
            folder_name = Link.get_folder_name(type=Link.LINK_FOLDER, text_with_full_link=description)
            file_path = self.folder_manager.get_path(folder=EnvFolders.get_by_name(folder_name))
            if file_path:
                link = self.folder_manager.get_link(file_path, is_path_folder=True)
        elif Link.LINK_FILE_SETTING.value in description:
            folder_name = Link.get_folder_name(type=Link.LINK_FILE_SETTING, text_with_full_link=description)
            file_path = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.get_by_name(folder_name))
            if file_path:
                link = self.folder_manager.get_link(file_path)
        if link:
            self.help_links.append({"title":title, "link":link})
        return

    
    def create_help_panel(self, dict_text_help: dict[str, str], panel_name:str ="help") -> str:
        title_and_description = int((len(dict_text_help.keys()) / len(self.available_language.keys())) / 2)
        text_help = Text()
        self.help_links:list[dict[str,str]] = [] 
        
        title_help_text = None
        for step in range(title_and_description):
            title_key = f"step_{step}_title_{self.current_language}"
            description_key = f"step_{step}_description_{self.current_language}"
            title = dict_text_help.get(title_key, "No title available")
            description = dict_text_help.get(description_key, "No description available")
            if any(keyword.value in description for keyword in self.keywords_links):
                self.extract_link(title, description)
                continue
            
            title_help_text = f"\n{step + 1}: {title}\n"
            description_help_text = f"{description}\n"
            text_help.append(Text(title_help_text, style="green"))
            text_help.append(Text(description_help_text, style="white"))
        
        # Creating a panel with the accumulated text
        if title_help_text:
            panel_help = Panel(text_help, title="Help Information", title_align="left")
            ratio_help = self.update_length_console(content=panel_help)
            self.main_layout.add_split(Layout(name=panel_name, ratio=ratio_help))
            self.main_layout[panel_name].update(panel_help)

        if self.help_links:
            for n, help_link in enumerate(self.help_links):
                centered_link = Align.center(f"[blue]{help_link['link']}[/blue]")
                panel_link = Panel(centered_link, title=help_link['title'], style="white",  title_align="left")
                ratio_link = self.update_length_console(content=panel_link)
                self.main_layout.add_split(Layout(name=f"{str(n)}_{panel_name}_link", ratio=ratio_link))
                self.main_layout[f"{str(n)}_{panel_name}_link"].update(panel_link)

    def create_table(self, data_items: dict[any, any], items_setting:list[ItemTableSetting], table_setting:TableSetting, panel_name:str) -> Table:
        
        def replace_underscore(k):
            if not isinstance(k, str) :  
                return k
            key = k[0].upper() + k[1:]
            return key.replace("_", " ")
        
        def replace_none(v, value_replace):
            if isinstance(v, NoneType):
                return value_replace
            return v
        
        table = Table(padding=(0, 1), 
                      show_lines=True,
                      title= Text(text=table_setting.title, style= table_setting.style), box=box.MARKDOWN)
        
        def row_columns_items(key_dict:any, value:any) -> list[any]:
            rows_x_columns = []
            for item in items_setting:
                value_item = None
                row = item.row_setting
                if row.use_key:
                    value_item = key_dict
                else:
                    value_item = value
                if row.value_key and isinstance(value, dict):
                    value_item = value[row.value_key]
                if row.replace_underscore:
                    value_item = replace_underscore(k=value_item)
                if row.show_link_file and isinstance(value_item, str):
                    value_item = self.folder_manager.get_link(value_item, string_link=row.show_link_file)
                if row.use_row_number:
                    value_item = "*row_number*"
                if row.replace_none:
                    value_item = replace_none(v=value_item, value_replace=row.replace_none)

                rows_x_columns.append(value_item)
                
            return rows_x_columns
            
        for item in items_setting:
            column = item.column_setting
            table.add_column(column.title, style=column.column_style, overflow=column.overflow, no_wrap=column.no_wrap)
        
        row_numb = 0
        for key, value in data_items.items():
            row_numb += 1
            list_items:list[str] = row_columns_items(key_dict=key, value=value)
            list_items = [str(row_numb) if x == "*row_number*" else str(x) for x in list_items]
            table.add_row(*list_items)
        
        panel_table = Panel(table, border_style= "bold green")
        ratio_table_panel = self.update_length_console(content=panel_table)
        self.main_layout.add_split(Layout(name=panel_name, ratio=ratio_table_panel))
        self.main_layout[panel_name].update(panel_table)
    
if __name__ == "__main__":
    
    data_table_one_dimension = {"key_1": "value_1",
                                "key_2": "value_3"}
    
    data_table_two_dimension = {"key_1": {"sub_key_1":"value_1_1",
                                          "sub_key_2":"value_1_2"},
                                
                                "key_2": {"sub_key_1":"---------",
                                          "sub_key_2":""},
                                
                                "key_3": {"sub_key_1":"value_2_1",
                                          "sub_key_2":"value_2_2"},
                                
                                "key_4": {"sub_key_1":"value_2_1",
                                          "sub_key_2":"value_2_2"},
                                
                                "key_5": {"sub_key_1":"value_2_1",
                                          "sub_key_2":"value_2_2nn"},
                                
                                }
    
    column_one_setting = ItemTableSetting(column_setting = ColumnTableSetting(title="Title Test 1"),
                                          row_setting=RowTableSetting(use_row_number=True) )
    
    column_two_setting = ItemTableSetting(column_setting = ColumnTableSetting(title="Title Test 2"),
                                          row_setting=RowTableSetting(replace_underscore=True, use_key=False, value_key="sub_key_2") )
    
    panel = SettingAreaPanel().show_panel(data_items=data_table_two_dimension, items_setting=[column_one_setting, column_two_setting] )
    #panel = Panel("panel_text", title="Help Information", title_align="left",)

    #calculate_lines(panel_width=100, content=panel, content_type="")
    
    #print(get_ratio(ratio_base=100, valor_base=100, valor_x=10))
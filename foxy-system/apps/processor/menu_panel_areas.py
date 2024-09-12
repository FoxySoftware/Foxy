import numpy as np
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress
from folder_manager import FolderManager, EnvFolders
from general_prompts import GeneralPrompts
from ocr_processor import OcrProcessor
from base_class.area_ocr_model import AreaOcrModel
from base_class.name_processor import NameProcessor
from screenshot_model import ImageModel, ScreenShotModel
from processor.resource_processor import text_general, text_step_help
from setting_area_panel import SettingAreaPanel
from settings_manager import SettingManager
from base_class.table_models import (ColumnTableSetting, 
                                            ItemTableSetting, RowTableSetting, TableSetting)

class PanelArea(GeneralPrompts, NameProcessor):
    
    def __init__(self, **kwargs) -> None:
        
        self.current_language:str = kwargs.get("current_language", "EN")
        self._folder_manager:callable =  kwargs["folder_manager"]
        self._setting_manager:callable = kwargs["setting_manager"]
        self._setting_area_panel:callable  = kwargs["setting_area_panel"]
        self._ocr_processor:callable  = kwargs["ocr_processor"]
        self.option_automatic_next:str = text_general.map[f'option_automatic_next_{self.current_language}']
        self.option_back_to_menu_area:str = text_general.map[f'option_back_to_menu_area_{self.current_language}']
        
        super().__init__( **kwargs)

    
    @property
    def folder_manager(self) -> FolderManager:
        return self._folder_manager()

    @property
    def setting_manager(self) -> SettingManager: 
        return self._setting_manager()

    @property
    def setting_area_panel(self)-> SettingAreaPanel:
        return self._setting_area_panel()

    @property
    def ocr_processor(self)-> OcrProcessor:
        return self._ocr_processor()
    
    def panel_test_ocr(self, area_model:AreaOcrModel, lang_area_model:str = "en") -> bool:
        # MARK: TEST AREAS
        console = Console(height=5)

        def check_files_test():
            if self.folder_manager.count_files_with_extension(folder=EnvFolders.IMAGES_SETTING_TESTING, extension= ".png") == 0:
                link_folder_captures = self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.CAPTURES) , is_path_folder= True)
                link_folder_test = self.folder_manager.get_link(path=self.folder_manager.get_path(folder=EnvFolders.IMAGES_SETTING_TESTING) , is_path_folder= True)
                text= text_general.map[f"help_empty_test_image_files_{self.current_language}"]
                text = text.replace("*path_capture_folder", f"[blue]{link_folder_captures}[/blue]")
                text = text.replace("*path_test_folder", f"[blue]{link_folder_test}[/blue]")
                #console.clear()
                console.print(Panel(text, style="yellow"))
                option = self.prompt_options(default_option=self.option_automatic_next,
                                                others_options=[self.option_back_to_menu_area],
                                                message=text_general.map[f"message_to_continue_{self.current_language}"] )
                return option
                
                
        option = check_files_test()
        
        if option == self.option_automatic_next:
            return self.panel_test_ocr(area_model=area_model)
        if option == self.option_back_to_menu_area:
            return True
        
        title = f"📋 ➔ {self.get_full_name_area(area_model)}" 
      
        

        list_test_image = self.setting_manager.get_setting_images()
        # dict_image_info = {"name":None,"path":None, "image":None}
        dict_data = {}
        screen_id = self.setting_manager.screen_id
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Processing {len(list_test_image)} Images", total=len(list_test_image))

            for n, test_image_dict in  enumerate(list_test_image):
                image_name:str = test_image_dict["name"]
                image_path:str = test_image_dict["path"]
                image:np.ndarray = test_image_dict["image"]
                image_source = ImageModel(
                    name=image_name,
                    image=image,
                    path=image_path,
                    
                )
                screenshot_model = ScreenShotModel(
                    screen_id= screen_id,
                    folder_manager=self.folder_manager,
                    test_mode=True,
                    image_source_model=image_source,
                    list_area_model=[area_model]
                )
                screenshot_model = self.ocr_processor.main_ocr_process(screenshot_model=screenshot_model)
                area_model = screenshot_model.list_area_model[0]
                progress.update(task, advance=1)
                dict_data[image_name] = {"path_image":image_path, 
                                        "cropped_image_path":area_model.path_image_cropped.value,
                                        "ocr_raw_value": area_model.ocr_raw_value.value,
                                        "final_value":area_model.final_value.value}

        t_setting = TableSetting(title=title, style="bold yellow on black")
        
        column_no = ItemTableSetting(column_setting = ColumnTableSetting(title="No.",
                                                                         column_style="green"),
                                          row_setting=RowTableSetting(use_row_number=True
                                                                      ) )
    
        column_image_source = ItemTableSetting(column_setting = ColumnTableSetting(title="Test Image Source",
                                                                                  column_style="blue"),
                                                  row_setting=RowTableSetting(value_key="path_image",
                                                                      show_link_file="Image",))
                                              
        column_image_cropped = ItemTableSetting(column_setting = ColumnTableSetting(title="Image Area Cropped",
                                                                                  column_style="blue"),
                                                row_setting=RowTableSetting(value_key="cropped_image_path",
                                                                        show_link_file="Image") )

        column_raw_value = ItemTableSetting(column_setting = ColumnTableSetting(title="String Recognized in Area",
                                                                                  column_style="white"),
                                            row_setting=RowTableSetting(value_key="ocr_raw_value",
                                                                      ))
        
        column_final_value = ItemTableSetting(column_setting = ColumnTableSetting(title="Final value",
                                                                                  column_style="white"),
                                            row_setting=RowTableSetting(value_key="final_value",
                                                                      ))
        
        
        self.setting_area_panel.add_panel(data_items=dict_data,
                                           dict_help=text_step_help.help_test_area,
                                           table_setting=t_setting,
                                           items_setting=[
                                               column_no,
                                               column_image_source,
                                               column_image_cropped,
                                               column_raw_value,
                                               column_final_value
                                           ])
        return False
    
    def panel_area_model(self,area_model:AreaOcrModel, dict_help:dict[str,str]):
        # MARK: SHOW PANEL AREA MODEL

        data_dict = area_model.to_dict_key_value_visible()
        settings_user_input = {key: value for  key, value in data_dict.items() if value["input_user"]}
        
        title = f"🛠️ ➔ {self.get_full_name_area(area_model)}" 

        
        t_setting = TableSetting(title=title, style="bold blue on black")
        
        column_option = ItemTableSetting(column_setting = ColumnTableSetting(title="Option",
                                                                             column_style="green"
                                                                             ),
                                          row_setting=RowTableSetting(use_row_number=True
                                                                      ) )
    
        column_setting = ItemTableSetting(column_setting = ColumnTableSetting(title="Setting",
                                                                                  column_style="bold white"),
                                                  row_setting=RowTableSetting(use_key=True,
                                                                      replace_underscore=True,
                                          ))
                                              
        column_value = ItemTableSetting(column_setting = ColumnTableSetting(title="Value",
                                                                                  column_style="bold green"),
                                            row_setting=RowTableSetting(value_key="value",
                                                                        replace_none= " "

                                                                      ) )

        column_description = ItemTableSetting(column_setting = ColumnTableSetting(title="Description",
                                                                                  column_style="white"),
                                            row_setting=RowTableSetting(value_key="description",
                                                                      ) )
        self.setting_area_panel.show_panel(data_items=settings_user_input ,
                                           dict_help=dict_help,
                                           table_setting=t_setting,
                                           items_setting=[
                                               column_option,
                                               column_setting,
                                               column_value,
                                               column_description
                                           ])
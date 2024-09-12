from dataclasses import dataclass
import os
import time
from concept_test.csv_creator import CsvCreator
from concept_test.xlsx_creator import XlsxCreator
from folder_manager import FolderManager

@dataclass
class SettingsAreasFile:
    
    project_name:str
    image_mask_rectangles_path:str
    labelled_image_name:str
    xlsx_file_name:str
    unix_time:int

    def __init__(self,
                 project_name:str,
                 folder_manger:FolderManager,
                 image_mask_rectangles_path:str,
                 labelled_image_name:str,
                 xlsx_file_name:str,
                 unix_time:int = int(time.time())):
        
        self.project_name = project_name
        self.folder_manager = folder_manger
        self.image_mask_rectangles_path = image_mask_rectangles_path
        self.labelled_image_name = labelled_image_name
        self.xlsx_file_name = xlsx_file_name
        self.unix_time = unix_time
        
    def __create_csv_file(self, list_map_rectangle:list[dict[str, any]]) -> str:
        csv_file_name =self.xlsx_file_name.replace('.xlsx', '.csv')
        csv_creator = CsvCreator(self.folder_manager, csv_file_name, self.unix_time)
        csv_file_path = csv_creator.create_map_rectangle_csv(list_map_rectangle)
        return csv_file_path, csv_creator.unix_time

    def __create_xlsx_file(self, csv_file_path:str, unix_time:int) -> str:

        xlsxCreator = XlsxCreator(self.folder_manager, 
                                  f'{str(unix_time)}_{self.xlsx_file_name}',
                                    unix_time)
        
        xlsxCreator.cvs_to_xlsx(csv_file_path=csv_file_path,
                                column_title_in_row=0,
                                column_type_in_row=1,
                                column_description_in_row=2)
        
        xlsxCreator.close()
        return xlsxCreator.path
    
    def create_mask_data_map_xlsx(self, list_map_rectangle:list[dict[str, any]], csv_file_path:str|None=None,):
        if not csv_file_path or not os.path.exists(csv_file_path):
            csv_file_path, unix_time= self.__create_csv_file(list_map_rectangle)
        xlsx_file_path = self.__create_xlsx_file(csv_file_path, unix_time)
        return csv_file_path, xlsx_file_path
    
    def xlsx_to_dict(self, xlsx_file_path:str, csv_file_path:str) -> list[dict[str, any]]:
        xlsxCreator = XlsxCreator(self.folder_manager, xlsx_file_path)
        xlsxCreator.xlsx_to_csv(xlsx_file_path, csv_file_path)
        csvCreator = CsvCreator(self.folder_manager, csv_file_path)
        list_dict_map = csvCreator.csv_to_dict(csv_file_path)
        return list_dict_map
    
    
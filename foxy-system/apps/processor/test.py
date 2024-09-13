import re

from base_class.area_ocr_model import AreaOcrModel

# def replace_last_occurrence(s, old, new)->str:
#     parts = s.rsplit(old, 1)  
#     return new.join(parts)



# name = "5_pe54pepe"


# new_name = replace_last_occurrence(name, "3", "JAJA")



# def extract_numbers_from_string(s) -> list[int]:
#     return [int(num) for num in re.findall(r'\d+', s)]



# print(new_name)

# list_int = extract_numbers_from_string(new_name)[-1]
# print(list_int)

from types import NoneType


a = None
print(type(None))

if isinstance(a, NoneType):
    print("is instance of NoneType")
    
    
area_1 = AreaOcrModel()
area_1.name.set_value("area_1")
area_1.group_name.set_value("area_group_1")

area_2 = AreaOcrModel()
area_2.name.set_value("area_2")
area_2.group_name.set_value("area_group_1")

area_3 = AreaOcrModel()
area_3.name.set_value("area_without_group")

area_x = AreaOcrModel()
area_x.name.set_value("area_without_group_1")

area_4 = AreaOcrModel()
area_4.name.set_value("area_1")
area_4.group_name.set_value("area_group_2")

area_5 = AreaOcrModel()
area_5.name.set_value("area_2")
area_5.group_name.set_value("area_group_2")

list_areas_model:list[AreaOcrModel] = [area_1, area_2, area_3, area_4, area_5, area_x] 

def replace_last_occurrence(s, old, new)->str:
        parts = s.rsplit(old, 1)  
        return new.join(parts)

def contains_number(s) -> bool:
    return bool(re.search(r'\d', s))

def extract_numbers_from_string(s) -> list[int]:
    return [int(num) for num in re.findall(r'\d+', s)]

def check_if_name_is_unique(new_name_area:str, group_name_source:str | None ) -> bool:
    list_area_coincidence = [area for area in list_areas_model if area.name.value == new_name_area and area.group_name.value == group_name_source]
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
        new_name_area = name_area_model + "_1"
        while is_no_unique_name:
            is_no_unique_name = not check_if_name_is_unique(new_name_area, area_model.group_name.value)
            
            if is_no_unique_name:
                number_of_name = extract_numbers_from_string(new_name_area)[-1] + 1
                new_name_area = replace_last_occurrence(new_name_area, str(number_of_name - 1), str(number_of_name))
        
    
    return new_name_area


new_name = get_new_name_area(area_1)
print(f"name area source : {area_1.name.value}")
print(f"new name : {new_name}")


new_name = get_new_name_area(area_3)
print(f"name area source : {area_3.name.value}")
print(f"new name : {new_name}")

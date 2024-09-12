
from dataclasses import dataclass
from types import NoneType


@dataclass
class StandardDataModel:
    type:str
    description:str
    purpose:str = None
    default:any = None
    __value:any = None
    input_user:bool = None
    required:bool  = None
    hide:bool  = None
    options:set[any] = None
    key_name_final:str = None
    
    @property
    def value(cls) -> any:
        if isinstance(cls.__value, NoneType):
            return cls.default
        return cls.__value
    
    @property
    def options_str(cls) -> str | NoneType:
        if not cls.options:
            return None
        option_list = list(cls.options)
        return "".join([str(item) for item in option_list])
    
    def set_value(self, value):
        self.__value = value
    
    
    @property
    def to_dict(self):
        return {"type":self.type, "description":self.description, "value":self.__value}

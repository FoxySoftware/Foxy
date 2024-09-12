from dataclasses import dataclass
from enum import Enum


@dataclass
class Resolution(Enum):
    HD = (1280, 720)
    FULL_HD = (1920, 1080)
    TWO_K = (2560, 1440)
    FOUR_K = (3840, 2160)
    FIVE_K = (5120, 2880)
    CUSTOM = (0, 0)  # Placeholder for custom resolution

    def __new__(cls, width: int, height: int):
        # Create an instance of the class
        obj = object.__new__(cls)
        obj._value_ = (width, height)
        return obj
    
    @classmethod
    def from_string(cls, value:str):
        for resolution in cls:
            if resolution.name == value:
                return cls._from_name(name=value)
        return cls._from_str_width_height(tuple_str=value)

    @classmethod
    def _from_str_width_height(cls, tuple_str: str) -> 'Resolution':
        def numbers(value: str) -> str:
            return ''.join(filter(str.isdigit, value))

        width_str = "0"
        height_str = "0"
        divisors = [",", "x"]
        for div in divisors:
            if div in tuple_str:
                width_str = tuple_str.split(div)[0]
                height_str = tuple_str.split(div)[1]
                break
        width = int(numbers(value=width_str))
        height = int(numbers(value=height_str))

        # Check if the resolution matches any predefined ones
        for resolution in cls:
            if resolution.value == (width, height):
                return resolution

        # Create and return a CUSTOM resolution
        custom_resolution = Resolution.CUSTOM
        custom_resolution._value_ = (width, height)
        return custom_resolution
    
    @property
    def string_value(self) -> str:
        """Return the resolution as a formatted string with its reference."""
        return f"{self.name.replace('_', ' ')}: {self.value[0]} x {self.value[1]}"

    @property
    def reference_string(self) -> str:
        """Return the resolution reference with a descriptive format."""
        return f"Resolution {self.name.replace('_', ' ')} is {self.value[0]} pixels wide and {self.value[1]} pixels high."
    
    @classmethod
    def _from_name(cls, name: str)-> "Resolution":
        try:
            # Match the name with the enum members
            return cls[name]
        except KeyError:
            raise ValueError(f"No ScreenResolution found for string '{name}'")


if __name__ == "__main__":
    
    res1 = Resolution.from_string("CUSTOM")
    
    print(res1.name)
    print(res1.string_value)
    print(res1.reference_string)
    print(res1.value)
from enum import Enum


class SourceMode(Enum):
    WEB = "WEB"
    VIDEO = "VIDEO"
    
    @classmethod
    def _from_name(cls, name: str)-> "SourceMode":
        try:
            # Match the name with the enum members
            return cls[name]
        except KeyError:
            raise ValueError(f"No ModeSource found for string '{name}'")

    
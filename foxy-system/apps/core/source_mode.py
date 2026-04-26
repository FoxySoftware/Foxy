from enum import Enum


class SourceMode(Enum):
    WEB = "WEB"
    VIDEO = "VIDEO"

    @classmethod
    def _from_name(cls, name: str) -> "SourceMode":
        try:
            return cls[name]
        except KeyError:
            raise ValueError(f"No SourceMode found for string '{name}'")


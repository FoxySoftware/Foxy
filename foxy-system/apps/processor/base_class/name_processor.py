from resource_processor import text_general
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from area_ocr_model import AreaOcrModel

MIDDLE_SYMBOL = " ∈ "  # BELONG TO A SET.
SET_SYMBOL = "⋓"


class NameProcessor:
    def __init__(self, **kwargs) -> None:    
        self.current_language:str = kwargs.get("current_language", "EN")
    
    
    @staticmethod
    def prefix(name: str) -> str:
        if name:
            return f"{name}{MIDDLE_SYMBOL}"
        return ""

    @staticmethod
    def suffix(name: str) -> str:
        if name:
            return f"{MIDDLE_SYMBOL}{name}"
        return ""

    def name_with_suffix_or_name(self, name: str, suffix_name: str | None) -> str:
        if not name:
            raise ValueError("Name is required")
        suffix_str = self.suffix(suffix_name) if suffix_name else ""
        return f"{name}{suffix_str}"

    def name_with_prefix_or_name(self, name: str, prefix_name: str | None) -> str:
        if not name:
            raise ValueError("Name is required")
        prefix_str = self.prefix(prefix_name) if prefix_name else ""
        return f"{prefix_str}{name}"

    def get_full_name_area(self, area_model: "AreaOcrModel", without_n_area=False):
        key = str(area_model.key.value)
        base_name = f"{text_general.map[f'area_number_{self.current_language}']}: {key}"

        name = area_model.name.value
        group_name = area_model.group_name.value

        if without_n_area:
            if group_name:
                return f"{group_name}{MIDDLE_SYMBOL}{name}" if name else group_name
            return name if name else base_name

        if name and group_name:
            return f"{base_name} - {group_name}{MIDDLE_SYMBOL}{name}"
        elif name:
            return f"{base_name} - {name}"

        return base_name
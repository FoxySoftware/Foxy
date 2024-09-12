from dataclasses import dataclass


@dataclass
class RowTableSetting():
    # row arguments for the row 
    use_key: bool = True # use the key of the dict_data
    use_row_number:bool = False
    value_key: str | None = None # If the value of the data is another dictionary, set a key to get an internal value.
    replace_none: str = ""
    replace_underscore: bool = False
    show_link_file: str = None
    
    @classmethod
    def default(cls) -> "RowTableSetting":
        return cls(
            use_key=True,
            value_key=None,
            replace_none= "",
            replace_underscore=False,
            show_link_file= "ctr + click"
        )

@dataclass
class ColumnTableSetting:
    # arguments for the column 
    title: str = ""
    column_style: str ="bold cyan"
    overflow: str = "fold"
    no_wrap: bool = False
    
    @classmethod
    def default(cls) -> "ColumnTableSetting":
        return cls(
            title="Title Column",
            column_style="bold green",
            overflow="fold",
            no_wrap=False
        )
        
@dataclass
class ItemTableSetting:
    column_setting: ColumnTableSetting = ColumnTableSetting.default()
    row_setting: RowTableSetting = ColumnTableSetting.default()
    
    @classmethod
    def default(cls) -> "ItemTableSetting":
        return cls(
            column_setting=ColumnTableSetting.default(),
            row_setting=RowTableSetting.default()
        )

@dataclass
class TableSetting:
    title: str
    style: str = "bold cyan"
    
    @classmethod
    def default(cls) -> "TableSetting":
        return cls(
            title="Table title",
            style="bold cyan")
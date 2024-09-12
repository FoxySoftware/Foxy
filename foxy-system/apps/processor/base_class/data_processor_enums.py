from dataclasses import dataclass, field
from enum import Enum

class SqlType(Enum):
    INTEGER = 'INTEGER'
    REAL = 'REAL'
    TEXT = 'TEXT'
    

@dataclass
class TxDualIndex:
    # INDEX_0 OR INDEX_1 MUST BE PRESENT.
    
    INDEX_0: str = "KEY_TABLE_NAME"   # OPTIONAL, Represents the name of the first index TX. 
    INDEX_1: str = "KEY_COLUMN_NAME"  # OPTIONAL, Represents the name of the second index TX
    DEFAULT_VALUE_OF_0: str = ""  # Default value for the INDEX_0 KEY if THE VALUE IN DICT IS NONE
    DEFAULT_VALUE_OF_1: str = ""  # Default value for INDEX_1 KEY if THE VALUE IN DICT IS NONE
    

class StructureType(Enum):
    BOOLEAN:bool = True
    STRING:str = "--"
    INTEGER:int = 100
    DECIMAL:float = 1.1

@dataclass
class TxThirdIndexDimension:
    # List of index names for the third dimension
    LIST_INDEX: list[str] = field(default_factory=list, repr=True) 

@dataclass
class BaseUnpackKeys: 
    # List of keys used for unpacking data
    KEYS: list[str] = field(default_factory=list, repr=True)

@dataclass
class UnpackKeysToT2(BaseUnpackKeys): 
    pass

@dataclass
class UnpackKeysToTX(BaseUnpackKeys):
    pass

@dataclass
class AvoidUnpackKeysToT2(BaseUnpackKeys):
    pass

@dataclass
class AvoidUnpackKeysToTX(BaseUnpackKeys):
    pass

@dataclass
class DataStructureVar:
    """
    Represents the data structure and relationships between T1, T2, and TX tables.

    Structure Overview:
    --------------------
    - DICT_DATA_EXTRUCTURE_T1: dict[str, any]
    - DICT_DATA_EXTRUCTURE_T2_TX: dict[str, any]

    Relationships:
    ---------------
    - T1 (one) --- (many) T2
    - T2 (one) --- (many) TX

    Example Visualization:
    -----------------------
    T1
    └── T2
        ├── TX
        └── TX
    └── T2
        ├── TX
        └── TX
    

    _Attributes:
    ------------
    - `TYPE_PRIMARY_KEY_T1` (TypeStructure): Type of primary key for T1 (default: TEXT).
    - `TYPE_PRIMARY_KEY_T2` (TypeStructure): Type of primary key for T2 (default: TEXT).
    - `T1_NAME` (str): Default name for T1 tables.
    - `PRIMARY_KEY_T1` (str): Default primary key name for T1.
    - `T2_NAME` (str): Default name for T2 tables.
    - `PRIMARY_KEY_T2` (str): Default primary key name for T2.
    - `TX_DEFAULT_NAME` (str): Default name for TX tables.
    - `KEY_LIST_TABLE_TX` (str): Key for listing TX tables.
    - `TX_DUAL_INDEX` (dict): Contains index names for TX tables.
    - `DICT_DATA_EXTRUCTURE_T1` (dict[str, any]): Data structure for T1 (STRING | INTEGER).
    - `DICT_DATA_EXTRUCTURE_T2_TX` (dict[str, any]): Data structure for T2 and TX (STRING | INTEGER).
    - `TX_THIRD_INDEX_DIMENSION` (dict): Defines the third dimension index keys for TX.
    - `KEYS_TO_UNPACK_IN_DATA_DICT_T2` (list[str]): Keys to unpack specifically for T2 data.
    - `KEYS_TO_UNPACK_IN_TX` (list[str]): Keys to unpack specifically for TX data.
    - `KEYS_TO_AVOID_UNPACK_DATA_DICT_T2` (list[str]): Keys to avoid unpacking in T2 data.
    - `KEYS_TO_AVOID_UNPACK_IN_TX` (list[str]): Keys to avoid unpacking in TX data.
    - `SHARED_FOREIGN_KEY_T2_TX` (str): Indicates the foreign key shared between T2 and TX tables.    
    - `IS_SHARED_FOREIGN_KEY_IN_T2_PRIMARY_KEY: (bool): Indicates if the shared foreign key is a primary key in T2
    - `IS_SHARED_FOREIGN_KEY_IN_TX_PRIMARY_KEY` (bool): Indicates if the shared foreign key is a primary key in TX.
    """
        

    TYPE_PRIMARY_KEY_T1: SqlType = SqlType.TEXT
    TYPE_PRIMARY_KEY_T2: SqlType = SqlType.TEXT
    T1_NAME: str = "T1_NAME"
    PRIMARY_KEY_T1: str = "PRIMARY_KEY_T1"
    T2_NAME: str = "T2_NAME"
    PRIMARY_KEY_T2: str = "PRIMARY_KEY_T2"
    TX_DEFAULT_NAME: str = "TX_DEFAULT_NAME"
    KEY_LIST_TABLE_TX: str = "KEY_LIST_TABLE_TX"
    TX_DUAL_INDEX: TxDualIndex = TxDualIndex(INDEX_0="KEY_TABLE_NAME", INDEX_1="KEY_COLUMN_NAME")

    DICT_DATA_EXTRUCTURE_T1:dict[str,any] = None
    """
    {
        'PRIMARY_KEY_T1': TypeStructure.string.value | TypeStructure.integer.value,
        'KEY_1': TypeStructure.integer.value,
        'KEY_2': TypeStructure.decimal.value,
        '...KEY_N': TypeStructure.string.value
    }
    """
                                            
    DICT_DATA_EXTRUCTURE_T2_TX: dict[str,any] = None
    """
        {   'SHARED_FOREIGN_KEY_T1_T2:: TypeStructure.string.value | TypeStructure.integer.value,
            'PRIMARY_KEY_T2': TypeStructure.string.value | TypeStructure.integer.value,
            'KEYS_TO_UNPACK_IN_DATA_DICT_T2': {
                'KEY_1': TypeStructure.string.value,
                'KEY_2': TypeStructure.string.value,
                '..KEY_N': TypeStructure.boolean.value,
            },
            'KEY_LIST_TABLE_TX': [
                {
                    TX_DUAL_INDEX.INDEX_0: "TABLE_X_NAME",
                    TX_DUAL_INDEX.INDEX_1: "COLUMN_X_NAME",
                    '...KEY_N': TypeStructure.string.value,
                },
                {
                    TX_DUAL_INDEX.INDEX_0: "TABLE_X_NAME",
                    TX_DUAL_INDEX.INDEX_1: "COLUMN_X_NAME",
                    '...KEY_N': TypeStructure.string.value,
                }
            ]
        }
        """
    #ANY KEY IN 
    TX_THIRD_INDEX_DIMENSION: TxThirdIndexDimension = TxThirdIndexDimension(LIST_INDEX=['KEY_1', '...KEY_N'])

    KEYS_TO_UNPACK_IN_DATA_DICT_T2: UnpackKeysToT2 = field(default_factory=lambda: UnpackKeysToT2(KEYS=['KEY_1', '...KEY_N']))
    #ANY KEY PRESENT IN TX
    KEYS_TO_UNPACK_IN_TX: UnpackKeysToTX = field(default_factory=lambda: UnpackKeysToTX(KEYS=[]))
    #ANY KEY PRESENT IN T2 AND TX
    KEYS_TO_AVOID_UNPACK_DATA_DICT_T2: AvoidUnpackKeysToT2 = field(default_factory=lambda: AvoidUnpackKeysToT2(KEYS=[]))
    #ANY KEY PRESENT IN T2 
    KEYS_TO_AVOID_UNPACK_IN_TX: AvoidUnpackKeysToTX = field(default_factory=lambda: AvoidUnpackKeysToTX(KEYS=[]))
    
    SHARED_FOREIGN_KEY_T1_T2: str = PRIMARY_KEY_T1
    SHARED_FOREIGN_KEY_T2_TX: str = PRIMARY_KEY_T2
    
    IS_SHARED_FOREIGN_KEY_IN_T2_PRIMARY_KEY: bool = False
    IS_SHARED_FOREIGN_KEY_IN_TX_PRIMARY_KEY: bool = True
    
    
    def validate_tx_dual_index(cls) -> bool:
        # Ensure that the data structure is properly initialized
        if cls.DICT_DATA_EXTRUCTURE_T2_TX is None:
            return False
        
        # Get the key list of TX tables
        tx_tables = cls.DICT_DATA_EXTRUCTURE_T2_TX.get(cls.KEY_LIST_TABLE_TX, [])
        
        # Extract keys for validation
        index_0_key = cls.TX_DUAL_INDEX.INDEX_0
        index_1_key = cls.TX_DUAL_INDEX.INDEX_1
        
        # Check each TX table dictionary for the presence of either INDEX_0 or INDEX_1
        for tx_table in tx_tables:
            if isinstance(tx_table, dict) and index_0_key not in tx_table and index_1_key not in tx_table:
                raise TxDualIndexMissingError(
                    missing_key=f"{index_0_key} or {index_1_key}",
                    dict_name='DICT_DATA_EXTRUCTURE_T2_TX',
                    list_key=cls.KEY_LIST_TABLE_TX
                )
        
        return True
    
class TxDualIndexMissingError(Exception):
    def __init__(self, missing_key: str, dict_name: str, list_key: str):
        self.missing_key = missing_key
        self.dict_name = dict_name
        self.list_key = list_key
        message = (
            f"The key '{self.missing_key}' must be present in all dictionary items of "
            f"'{self.dict_name}[{self.list_key}]'. Ensure that every item in the list contains this key."
        )
        super().__init__(message)
        
    

if __name__ == "__main__":
    
    
    try:
        tx_dual = TxDualIndex(INDEX_1="KEY_COLUMN_NAME")
        a = DataStructureVar(DICT_DATA_EXTRUCTURE_T2_TX = {
            'SHARED_FOREIGN_KEY_T1_T2':StructureType.STRING,   
            'PRIMARY_KEY_T2':StructureType.STRING,
            'KEYS_TO_UNPACK_IN_DATA_DICT_T2': {
                'KEY_1': StructureType.STRING,
                'KEY_2': StructureType.STRING,
                '..KEY_N': StructureType.BOOLEAN, },
            'KEY_LIST_TABLE_TX': [{tx_dual.INDEX_0:"TABLE_X_NAME_V",
                                    "other_tx_dual":"COLUMN_X_NAME_V",
                                    '...KEY_N': StructureType.STRING},
                                    {
                                    '...KEY_N':"COLUMN_X_NAME_V",
                                    '...KEY_N': StructureType.STRING}] })
        a.validate_tx_dual_index()
        raise Exception("!!!! TxDualIndexMissingError no works")
    except TxDualIndexMissingError as e:
        print(f"Is OK ! . TxDualIndexMissingError Works {e} ")
        
        
        
    tx_dual = TxDualIndex(INDEX_1="KEY_COLUMN_NAME")
    other_tx_dual =TxDualIndex(INDEX_1="KEY_COLUMN_NAME_X")
    a = DataStructureVar(DICT_DATA_EXTRUCTURE_T2_TX = {   
        'SHARED_FOREIGN_KEY_T1_T2':StructureType.STRING,   
        'PRIMARY_KEY_T2':StructureType.STRING,
        'KEYS_TO_UNPACK_IN_DATA_DICT_T2': {
            'KEY_1': StructureType.STRING,
            'KEY_2': StructureType.STRING,
            '..KEY_N': StructureType.BOOLEAN, },
        'KEY_LIST_TABLE_TX': [{tx_dual.INDEX_0:"TABLE_X_NAME_V",
                                tx_dual.INDEX_1:"COLUMN_X_NAME_V",
                                '...KEY_N': StructureType.STRING},
                                {'...KEY_N':"TABLE_X_NAME_V",
                                tx_dual.INDEX_1:"COLUMN_X_NAME_V",
                                '...KEY_N': StructureType.STRING}] })
        
    a.validate_tx_dual_index()

    
    a.KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS = ["A1", "A2"]
    a.TYPE_PRIMARY_KEY_T1 = SqlType.INTEGER
    # print("Instance A:")
    # print("KEY_LIST_TABLE_TX:", a.KEY_LIST_TABLE_TX)
    # print("KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS:", a.KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS)
    # print("TYPE_PRIMARY_KEY_T1:", a.TYPE_PRIMARY_KEY_T1)
    # print("---------------------------------")
    
    # b = DataStructureVar()
    # b.KEY_LIST_TABLE_TX = "B"
    # b.KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS = ["B1", "B2"]
    # b.TYPE_PRIMARY_KEY_T1 = SqlType.TEXT

    # print("Instance B:")
    # print("KEY_LIST_TABLE_TX:", b.KEY_LIST_TABLE_TX)
    # print("KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS:", b.KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS)
    # print("TYPE_PRIMARY_KEY_T1:", b.TYPE_PRIMARY_KEY_T1)
    
    # print("---------------------------------")
    # print("Rechecking Instance A:")
    # print("KEY_LIST_TABLE_TX:", a.KEY_LIST_TABLE_TX)
    # print("KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS:", a.KEYS_TO_AVOID_UNPACK_DATA_DICT_T2.KEYS)
    # print("TYPE_PRIMARY_KEY_T1:", a.TYPE_PRIMARY_KEY_T1)
    
    print(a.validate_tx_dual_index())

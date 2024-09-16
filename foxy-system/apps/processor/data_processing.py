import warnings
import pandas as pd
from base_class.data_processor_enums import TxDualIndex, TxThirdIndexDimension


warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)


class DataProcessing:
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def get_sqlite_type(value):
        if isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'REAL'
        elif isinstance(value, str):
            return 'TEXT'
        else:
            return 'TEXT'

    @staticmethod
    def _extend_list_columns_txs(entry_dict:dict,
                                 key_list_table_tx:str,
                                 keywords_to_get:list,
                                 keywords_to_ignore:list,
                                 tx_dual_index=TxDualIndex,
                                 tx_third_index_dimension=TxThirdIndexDimension):
        """
        Extend a list of transaction data (TX) with additional columns.
        
        Visualization:
        - input_dict
          |
          +-- key_list_table_tx
                |
                +-- list_to_extend
                      |
                      +-- (dict_column)
                            |
                            +-- (index_1, key)
                            +-- (list_index[0], value)
        """
        dict_to_include_in_txs = DataProcessing._filter_and_flattens_dict_from_keywords(entry_dict,
                                                            keywords_to_get=keywords_to_get,
                                                            keywords_to_ignore=keywords_to_ignore)
        
        list_to_extend = DataProcessing._create_list_to_extend_in_tx(dict_to_include_in_txs=dict_to_include_in_txs, 
                                                                    tx_dual_index=tx_dual_index,
                                                                    tx_third_index_dimension=tx_third_index_dimension)
        list_tx_data:list = entry_dict[key_list_table_tx]
        list_tx_data.extend(list_to_extend)
        
        return list_tx_data
    
    @staticmethod
    def _create_list_to_extend_in_tx( dict_to_include_in_txs:dict,
                                      tx_dual_index:TxDualIndex,
                                     tx_third_index_dimension:TxThirdIndexDimension):
        """
        Create a list of dictionaries to extend TX data.
        
        Visualization:
        - dict_to_include_in_txs
          |
          +-- (key, value)
                |
                +-- dict_column
                      |
                      +-- (index_1, key)
                      +-- (list_index[0], value)
        """
        
        list= []
        for key, value in dict_to_include_in_txs.items():
            dict_column = {tx_dual_index.INDEX_1:key, tx_third_index_dimension.LIST_INDEX[0]:value } 
            list.append(dict_column)
        
        return list
    
    @staticmethod
    def _filter_and_flattens_dict_from_keywords(input_dict:dict,
                                                keywords_to_get:list,
                                                keywords_to_ignore:list | None = None,
                                                include_parent_key=False, 
                                                char_middle:str = "_"):

        """
        Flatten and filter a dictionary based on specified keywords.
        
        Visualization:
        - input_dict
          |
          +-- (key, value)
                |
                +-- new_key (if matches keywords_to_get)
                |
                +-- (value if dict)
                      |
                      +-- sub_result
        """
        if keywords_to_ignore is None:
            keywords_to_ignore = []

        def recursive_filter(d, parent_key=''):
            result = {}
            for key, value in d.items():
                if key in keywords_to_ignore:
                    continue
                
                new_key = f"{parent_key}{char_middle}{key}" if parent_key and include_parent_key else key

                if any(keyword in str(key) for keyword in keywords_to_get):
                    result[new_key] = value

                if isinstance(value, dict):
                    sub_result = recursive_filter(value, new_key)
                    result.update(sub_result)

            return result

        return recursive_filter(input_dict)
    
    def _build_dictionary(self, dictionary_data: dict[str, str], 
                                keys_to_unpack: list[str] = None, 
                                keys_to_remove: list[str] = None,
                                additional_data: dict[str, str] = None):
    
        """
        Build a dictionary by unpacking and removing specified keys, and adding additional data.
        
        Visualization:
        - dictionary_data
          |
          +-- additional_data (if provided)
          |
          +-- keys_to_unpack (expand nested dicts)
          |
          +-- keys_to_remove (remove specified keys)
        """
    
        _dictionary_data = dictionary_data.copy()

        # Extend the dictionary with additional_data if provided
        if additional_data:
            _dictionary_data.update(additional_data)

        # Flatten dict *keys_to_unpack
        if keys_to_unpack:
            for key in keys_to_unpack:
                if key in _dictionary_data:
                    value_to_unpack = _dictionary_data.pop(key)
                    if isinstance(value_to_unpack, dict):
                        _dictionary_data.update(value_to_unpack)

        # Remove keys *keys_to_remove
        if keys_to_remove:
            for key in keys_to_remove:
                _dictionary_data.pop(key, None)

        return _dictionary_data

    @staticmethod
    def _update_dict_with_defaults(dict_source: dict, dict_default_values: dict):
        
        """
        Update a dictionary with default values if they are None.
        
        Visualization:
        - dict_source
          |
          +-- (key, value)
                |
                +-- dict_default_values (if key is None)
        """
        for key, value in dict_default_values.items():
            if key in dict_source and dict_source[key] is None:
                dict_source[key] = value
                
        return dict_source
    
    @staticmethod
    def create_data_frame_from_model(list_data: list[dict[str, any]],
                                    keywords_to_get:list,
                                    char_middle:str = "."
                                    ) -> pd.DataFrame:
        """
        Create a DataFrame from a list of dictionaries based on a model.
        
        Visualization:
        - list_data
          |
          +-- (entry)
                |
                +-- get_value_from_path
                |
                +-- transform_dict_keys
        """
        dict_model = DataProcessing._filter_and_flattens_dict_from_keywords(list_data[0],
                                                            keywords_to_get=keywords_to_get,
                                                            char_middle=char_middle,
                                                            include_parent_key=True )
        
        
        def transform_dict_keys(input_dict: dict) -> dict:
            transformed_dict = {}
            
            for key, value in input_dict.items():
                # Split the key by '.' to get the last part
                key_parts = key.split('.')
                final_key = key_parts[-1]  # Last part of the key
                transformed_dict[final_key] = key  # The original key as the value
            
            return transformed_dict
        
        dict_model = transform_dict_keys(dict_model)

        def get_value_from_path(data: dict[str, any], path: str) -> any:
            keys = path.split(char_middle)
            value = data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
        
        columns = list(dict_model.keys())
        paths = list(dict_model.values())
        
        data = []
        
        for entry in list_data:
            row = {col: get_value_from_path(entry, path) for col, path in zip(columns, paths)}
            data.append(row)
        
        return pd.DataFrame(data)

    
    @staticmethod
    def _populate_data_frame_tx(super_list_data: list[list[dict[str, any]]],
                                df_model: pd.DataFrame,
                                list_keys: list[any], 
                                tx_dual_index: TxDualIndex = TxDualIndex(INDEX_0="group", INDEX_1="name"), 
                                third_dimension_index_keys: TxThirdIndexDimension = TxThirdIndexDimension(LIST_INDEX=["value"]),
                                ) -> pd.DataFrame:
        """
        Populate a DataFrame model with transaction data, improving performance.
        
        Visualization:
        - super_list_data
        |
        +-- (inner_data_list)
                |
                +-- (data)
                    |
                    +-- df_model
                            |
                            +-- (dimension_0, dimension_1, key)
        """
        updates = {}

        for index, inner_data_list in enumerate(super_list_data):
            for data in inner_data_list:
                dimension_0 = data.get(tx_dual_index.INDEX_0, tx_dual_index.DEFAULT_VALUE_OF_0) or tx_dual_index.DEFAULT_VALUE_OF_0
                dimension_1 = data.get(tx_dual_index.INDEX_1, tx_dual_index.DEFAULT_VALUE_OF_1) or tx_dual_index.DEFAULT_VALUE_OF_1

                if len(third_dimension_index_keys.LIST_INDEX) > 1:
                    for key in third_dimension_index_keys.LIST_INDEX:
                        updates[(list_keys[index], (dimension_0, dimension_1, key))] = data.get(key)
                else:
                    updates[(list_keys[index], (dimension_0, dimension_1))] = data.get(third_dimension_index_keys.LIST_INDEX[0])

    
        for (index, column), value in updates.items():
            df_model.loc[index, column] = value
                

        df_model = df_model.sort_index(axis=1)

        # Drop columns that are entirely NaN
        df_model = df_model.dropna(axis=1, how='all')

        return df_model
    
    
    
    @staticmethod
    def _create_multi_index_data_frame_model(list_dict_model:list[dict[str,any]],
                                            tx_dual_index:TxDualIndex = TxDualIndex(INDEX_0="group", INDEX_1="name"), 
                                            third_dimension_index_keys:TxThirdIndexDimension = TxThirdIndexDimension(LIST_INDEX=["value"]),
                                            with_data=True,
                                            shared_foreign_key:any=0) -> pd.DataFrame: 
        
        """
        Create a DataFrame model with multi-index or single index.
        
        Visualization:
        - data_model
          |
          +-- columns
                |
                +-- pd.MultiIndex or pd.Index
        """
        if len(third_dimension_index_keys.LIST_INDEX) > 1:
            # Create MultiIndex with thirds dimension Where the value of the first dimension is not present replace with 
            columns = pd.MultiIndex.from_tuples(
                [(d.get(tx_dual_index.INDEX_0, tx_dual_index.DEFAULT_VALUE_OF_0) or tx_dual_index.DEFAULT_VALUE_OF_0,
                  d.get(tx_dual_index.INDEX_1, tx_dual_index.DEFAULT_VALUE_OF_1) or tx_dual_index.DEFAULT_VALUE_OF_1, key) 
                 for d in list_dict_model for key in third_dimension_index_keys.LIST_INDEX]
            )
        else:
            # Create a bidirectional Index
            columns = pd.Index(
                [(d.get(tx_dual_index.INDEX_0, tx_dual_index.DEFAULT_VALUE_OF_0) or tx_dual_index.DEFAULT_VALUE_OF_0,
                  d.get(tx_dual_index.INDEX_1, tx_dual_index.DEFAULT_VALUE_OF_1) or tx_dual_index.DEFAULT_VALUE_OF_1) for d in list_dict_model]
            )

        # Create the DataFrame 
        df_model = pd.DataFrame(columns=columns)
        
        
        # Populate df.
        if with_data:
            df_model = DataProcessing._populate_data_frame_tx(super_list_data=[list_dict_model],
                                                              df_model=df_model,
                                                              list_keys=[shared_foreign_key],
                                                              tx_dual_index=tx_dual_index,
                                                              third_dimension_index_keys=third_dimension_index_keys,
                                                              )
            
        df_model = df_model.dropna(axis=1, how='all')
        return df_model


if __name__ == "__main__":
    _list_key = ["image_1", "image_2"]
    _data = [[  
              {'area_number': 2, 'name': 'ALTITUDE', 'group': 'STAGE_1', 'value': 100, 'raw_value': "100", 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_22.png'},
                {'area_number': 3, 'name': 'SPEED', 'group': 'STAGE_1', 'value': 200, 'raw_value': '200', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_33.png'},
                {'area_number': 0, 'name': 'ALTITUDE', 'group': 'STAGE_2', 'value': 300, 'raw_value': '300', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_00.png'},
                {'area_number': 4, 'name': 'SPEED', 'group': 'STAGE_2', 'value': 400, 'raw_value': '400', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_44.png'},
                {'area_number': 1, 'name': 'TIME_LAPSE', 'group': None, 'value': 'T+00:00:13', 'raw_value': 'T+00:00:13', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_11.png'}
                ],
             
             [  
              {'area_number': 2, 'name': 'ALTITUDE', 'group': 'STAGE_1', 'value': 500, 'raw_value': "500", 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_22.png'},
                {'area_number': 3, 'name': 'SPEED', 'group': 'STAGE_1', 'value': 600, 'raw_value': '600', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_33.png'},
                {'area_number': 0, 'name': 'ALTITUDE', 'group': 'STAGE_2', 'value': 700, 'raw_value': '700', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_00.png'},
                {'area_number': 4, 'name': 'SPEED', 'group': 'STAGE_2', 'value': 800, 'raw_value': '800', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_44.png'},
                {'area_number': 1, 'name': 'TIME_LAPSE', 'group': None, 'value': 'T+00:00:14', 'raw_value': 'T+00:00:14', 'path_image': 'ProjectFiles/ift4_starship/D_CROPPED_IMAGES_OCR/3_agf_30-08-2024_ift4_starship_web/source_IFP_21_1725031126.3294787_change_detected_area_no_11.png'}
                ],
             
             ]
    modeling = DataProcessing()
    df = modeling._create_multi_index_data_frame_model(list_dict_model=_data[0], with_data=False, )
    df_with_data = modeling._populate_data_frame_tx(super_list_data=_data, df_model=df, list_keys=_list_key)
    #modeling.create_database_by_data_frame_model(df_model=df)
    print(df_with_data)
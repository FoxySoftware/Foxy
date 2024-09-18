import configparser

class ConfigManager:
    def __init__(self, filename):
        self.filename = filename
        self.config = configparser.ConfigParser(interpolation=None)
        
    def save_dict_to_ini(self, data_dict):
        for section, options in data_dict.items():
            self.config[section] = options
        with open(self.filename, 'w') as config_file:
            self.config.write(config_file)

    def load_ini_to_dict(self):
        try:
            self.config.read(self.filename)
            data_dict = {section: dict(self.config.items(section)) for section in self.config.sections()}
        except Exception :
            return {}    
        return data_dict
    
    def get_dict_section(self, section_name:str):
        try:
            self.config.read(self.filename)
            data_dict = {section: dict(self.config.items(section)) for section in self.config.sections() if section == section_name}
        except Exception :
            return {}    
        return data_dict
    

    def update_section(self, section: str, data_dict: dict[str, any]) -> None:
        """Update or create a section in the INI file."""
        self.config.read(self.filename)
        
        if section not in self.config:
            self.config.add_section(section)
        
        for key, value in data_dict.items():
            self.config[section][key] = str(value)

        with open(self.filename, 'w') as config_file:
            self.config.write(config_file)
    
    def clear_file(self):
        with open(self.filename, 'w') as file:
            self.config.write(file)

# if __name__ == "__main__":
#     config_manager = ConfigManager('config.ini')
#     config_data = {
#     'Section1': {'key1': 'value1', 'key2': 'value2'},
#     'Section2': {'keyA': 'valueA', 'keyB': 'valueB'}
# }
#     config_manager.save_dict_to_ini(config_data)

#     loaded_config_data = config_manager.load_ini_to_dict()
#     print(loaded_config_data)

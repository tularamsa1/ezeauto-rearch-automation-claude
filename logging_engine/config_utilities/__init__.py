from . import yaml_utils as yaml
from ..globals import CONFIG_FILEPATH

# print(CONFIG_FILEPATH)


class Config:

    def __init__(self, file_path=CONFIG_FILEPATH) -> None:
        self._config_filepath = file_path
        # self.create_default_yaml_configuration_file()
        self._config = self.load_from_yaml(self._config_filepath)
        return

    def load_from_yaml(self, file_path) -> dict:
        '''
        Loads the configuration from the yaml file
        '''

        config = yaml.load_configuration_file(file_path)
        config = yaml.prepare_config_settings(config) # here regenerating config happens
        return config


    def create_default_yaml_configuration_file(self) -> None:
        '''
        Creates a default configuration file for the application
        '''
        yaml.create_default_configuration_file()
        return
    
    @property
    def settings(self) -> dict:
        return self._config
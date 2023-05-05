import os
import yaml

from .path import CONFIGURATION_YAML_FILE_PATH



def load_configuration():
    with open(CONFIGURATION_YAML_FILE_PATH, 'r') as f:
        return yaml.safe_load(f)

def save_configuration(config: dict):
    with open(CONFIGURATION_YAML_FILE_PATH, 'w') as f:
        yaml.dump(config, f, sort_keys=False)




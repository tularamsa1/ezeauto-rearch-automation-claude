from datetime import datetime
import os

# relative imports
from configparser import ConfigParser

# relative imports
from ..globals import ROOT_DIR


def get_log_file_path():
    """
    Get the log file path from the ExecutionDirectories.conf config file in Runtime folder
    :return: log_file_path: str
    """
    RUNTIME_DIR = os.path.join(ROOT_DIR, 'Runtime')
    EXECUTION_CONFIG_FILEPATH = os.path.join(RUNTIME_DIR, 'ExecutionDirectories.conf')

    config = ConfigParser()
    config.read(EXECUTION_CONFIG_FILEPATH)
    execution_log_dir = config.get("Logs", "executionlogpath")
    execution_log_filepath = os.path.join(execution_log_dir, 'EzeAuto.log')

    return execution_log_filepath




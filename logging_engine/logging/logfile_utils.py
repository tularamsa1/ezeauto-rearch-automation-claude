from datetime import datetime
import os

# relative imports
from configparser import ConfigParser

# relative imports
from ..globals import ROOT_DIR



# def create_log_file_dir():
#     """
#     Create the log file path according the date and time of execution
#     :return: log_file_path: str
#     """
#     LOG_DIR = os.path.join(ROOT_DIR, 'Logs')

#     # getting current date and time
#     now = datetime.now()
#     date_n_time = now.strftime("%Y-%m-%d %H:%M:%S")
#     date, time = date_n_time.split(' ')

#     # date, time

#     date_dir_name = f"ExecutionDate_{date}"
#     time_dir_name = f"ExecutionTime_{time}"


#     date_dir_path = os.path.join(LOG_DIR, date_dir_name)
#     time_dir_path = os.path.join(date_dir_path, time_dir_name)
#     log_file_dir = os.path.join(time_dir_path, 'ExecutionLog')

#     if not os.path.exists(date_dir_path):
#         os.mkdir(date_dir_path)
#     if not os.path.exists(time_dir_path):
#         os.mkdir(time_dir_path)
    
#     if not os.path.exists(log_file_dir):
#         os.mkdir(log_file_dir)

#     return log_file_dir


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




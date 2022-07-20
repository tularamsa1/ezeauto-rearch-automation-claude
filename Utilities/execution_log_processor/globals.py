import os


MAIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # path inside execution_log_processor
ROOT_DIR = os.path.dirname(MAIN_DIR)  # parent directory from where we can call the library

# other directories
CONFIG_DIR = os.path.join(ROOT_DIR, 'Configuration')
CONFIG_FILE = 'execution_log_config.yaml'
CONFIG_FILEPATH = os.path.join(CONFIG_DIR, CONFIG_FILE)


LOG_LINE_TAG = '<LogLine>'



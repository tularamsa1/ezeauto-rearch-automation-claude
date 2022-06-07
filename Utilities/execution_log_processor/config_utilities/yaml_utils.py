
import os
import yaml  # PyYAML==5.3.1 is currently used

# internal imports
from ..globals import CONFIG_DIR, CONFIG_FILE, LOG_LINE_TAG, CONFIG_FILEPATH

'''
YAML FILE RELATED FUNCTIONS
'''


def load_configuration_file(file_path) -> dict:
    """
    Load the configuration file
    :return: config: dict
    """
    with open(file_path) as f:
        config = yaml.safe_load(f)
        # print(config)
    return config


def prepare_config_settings(config:dict) -> dict:
    """
    Prepare the configuration settings to include the default values if not specified
    :param config: dict
    :return config: dict
    """

    config = load_configuration_file(CONFIG_FILEPATH)
    edited_config = {}

    edited_config['logLevel'] = config['logLevel']
    if config['useLogLineStartTag'] is True:
        edited_config['logFormat'] = f'''{LOG_LINE_TAG} {config['logFormat']}'''
    else:
        edited_config['logFormat'] = config['logFormat']
    edited_config['useLogLineStartTag'] = config['useLogLineStartTag']

    edited_config['useFileHandler'] = config['useFileHandler']
    edited_config['useConsoleHandler'] = config['useConsoleHandler']

    edited_config['fileHandler'] = {}
    edited_config['consoleHandler'] = {}

    if config['useFileHandler'] is True:
        
        # configure_file_handler_configurations(config, edited_config)
        # FILE LOG LEVEL
        if config['fileHandler']['logLevel'] == "DEFAULT":
            edited_config['fileHandler']['logLevel'] = config['logLevel']
        else:
            edited_config['fileHandler']['logLevel'] = config['fileHandler']['logLevel']
        
        # FILE LOG FORMAT
        if config['fileHandler']['logFormat'] == "DEFAULT":
            edited_config['fileHandler']['logFormat'] = config['logFormat']
        else:
            edited_config['fileHandler']['logFormat'] = config['fileHandler']['logFormat']
        
        # FILE LOG LINE TAG
        if config['fileHandler']['useLogLineStartTag'] == "DEFAULT":
            edited_config['fileHandler']['useLogLineStartTag'] = config['useLogLineStartTag']
        else:
            edited_config['fileHandler']['useLogLineStartTag'] = config['fileHandler']['useLogLineStartTag']

        # FILE LOG LINE TAG - FORMATING -- LOGLINES
        if edited_config['fileHandler']['useLogLineStartTag'] is True:
            edited_config['fileHandler']['logFormat'] =f'''{LOG_LINE_TAG} {edited_config['fileHandler']['logFormat']}'''
        elif edited_config['fileHandler']['useLogLineStartTag'] is False:
            edited_config['fileHandler']['logFormat'] = edited_config['fileHandler']['logFormat']

    else:
        edited_config['fileHandler'] = config['fileHandler']

    # IF CONSOLE HANDLER IS ENABLED ===========================================================================
    if config['useConsoleHandler'] is True:
        
        # configure_file_handler_configurations(config, edited_config)
        # FILE LOG LEVEL
        if config['consoleHandler']['logLevel'] == "DEFAULT":
            edited_config['consoleHandler']['logLevel'] = config['logLevel']
        else:
            edited_config['consoleHandler']['logLevel'] = config['consoleHandler']['logLevel']
        
        # FILE LOG FORMAT
        if config['consoleHandler']['logFormat'] == "DEFAULT":
            edited_config['consoleHandler']['logFormat'] = config['logFormat']
        else:
            edited_config['consoleHandler']['logFormat'] = config['consoleHandler']['logFormat']
        
        # FILE LOG LINE TAG
        if config['consoleHandler']['useLogLineStartTag'] == "DEFAULT":
            edited_config['consoleHandler']['useLogLineStartTag'] = config['useLogLineStartTag']
        else:
            edited_config['consoleHandler']['useLogLineStartTag'] = config['consoleHandler']['useLogLineStartTag']

        # FILE LOG LINE TAG - FORMATING -- LOGLINES
        if edited_config['consoleHandler']['useLogLineStartTag'] is True:
            edited_config['consoleHandler']['logFormat'] =f'''{LOG_LINE_TAG} {edited_config['consoleHandler']['logFormat']}'''
        elif edited_config['consoleHandler']['useLogLineStartTag'] is False:
            edited_config['consoleHandler']['logFormat'] = edited_config['consoleHandler']['logFormat']

    else:
        edited_config['consoleHandler'] = config['consoleHandler']
    # edited_config_filepath = os.path.join(CONFIG_DIR, 'edited_execution_log_config.yaml')
    # with open(edited_config_filepath, 'w') as f:
    #     yaml.dump(edited_config, f, default_flow_style=False, sort_keys=False, indent=2, line_break='',width=1000)
    return edited_config

def create_default_configuration_file():
    """
    Create a default configuration file for the application
    :return:
    """

    config = dict(
        logLevel = 'DEBUG',
        # logFile = 'execution_logs.log',
        logFormat = '''%(asctime)s | %(name)s | %(levelname)s (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s''',
        # handlers = ['fileHandler', 'consoleHandler'],
        useFileHandler = True,
        useConsoleHandler = True,
        useLogLineStartTag = True,

        fileHandler = dict(
            logLevel = 'DEFAULT', # this needed. if so it will take from general log level
            logFormat = 'DEFAULT',
            useLogLineStartTag = 'DEFAULT',
        ),

        consoleHandler = dict(
            logLevel = 'DEFAULT',
            logFormat = "DEFAULT",
            useLogLineStartTag = 'DEFAULT',
        ),

    )

    config_filepath = os.path.join(CONFIG_DIR, CONFIG_FILE)

    with open(config_filepath, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2, line_break='',width=1000)


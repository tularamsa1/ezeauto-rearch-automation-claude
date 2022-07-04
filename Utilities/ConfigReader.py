from configparser import ConfigParser
from DataProvider import GlobalConstants

automation_suite_path = GlobalConstants.EZEAUTO_MAIN_DIR

def read_config(section, key):
    config = ConfigParser()
    config.read(str(automation_suite_path)+"/Configuration/config.ini")
    return config.get(section, key)


def read_config_paths(section, key):
    config = ConfigParser()
    config.read(str(automation_suite_path)+"/Runtime/ExecutionDirectories.conf")
    return config.get(section, key)


def read_conf_with_spec_val(section, key, value):
    config = ConfigParser()
    config.read(str(automation_suite_path)+"/Configuration/config.ini")
    element = config.get(section, key)
    if "orgCode" in element:
        element = element.replace("orgCode",value)

    if "mobileNum" in element:
        element = element.replace("mobileNum", value)
    return element


def get_items_from_section(section):
    config = ConfigParser()
    config.read(str(automation_suite_path)+"/Configuration/config.ini")
    # return [config.get(section, key) for key in list_of_keys]
    return dict(config.items(section))
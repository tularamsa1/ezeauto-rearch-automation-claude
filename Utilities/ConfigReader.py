from os.path import dirname, abspath
from configparser import ConfigParser

automation_suite_path = dirname(dirname(abspath("./config.ini")))
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
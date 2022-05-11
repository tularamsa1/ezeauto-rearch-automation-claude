from Utilities import ConfigReader


def is_log_capture_required(locator):   # is_log_ss_capture_required  breakdown in two
    value = ConfigReader.read_config("logs", locator)
    return str(value)


def is_ss_capture_required(locator):   # is_log_ss_capture_required  breakdown in two
    # if str(locator).endswith("_ss"):
    value = ConfigReader.read_config("screenshots", locator)
    return str(value)


def get_environment(locator):   # get_environment
    value = ConfigReader.read_config("environment", locator)
    return str(value)


def pathToLogFile(locator):
    # if str(locator).__contains__("dev"):
    value = ConfigReader.read_config("path", locator)
    return str(value)
    # if str(locator).__contains__("demo1"):
    #     value = configReader.read_config("path", locator)
    #     return str(value)
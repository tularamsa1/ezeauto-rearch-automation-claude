from Utilities import configReader


def enter_data_logs(locator):
    if str(locator).endswith("_Logs"):
        value = configReader.read_config("logs", locator)
        return str(value)
    if str(locator).endswith("_ss"):
        value = configReader.read_config("logs", locator)
        return str(value)


def environment(locator):
    value = configReader.read_config("environment", locator)
    return str(value)


def pathToLogFile(locator):
    if str(locator).__contains__("dev"):
        value = configReader.read_config("path", locator)
        return str(value)
    if str(locator).__contains__("demo1"):
        value = configReader.read_config("path", locator)
        return str(value)
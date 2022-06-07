
from .base_handler import BaseHandler

class ConsoleHandler(BaseHandler):
    """
    ConsoleHandler class is used to load configuration specific to the cpnsole handler
    """
    def __init__(self, LogLevel, LogFormat, UseLogLineStartTag):
        super().__init__(LogLevel, LogFormat, UseLogLineStartTag)
        return


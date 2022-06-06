from .base_handler import BaseHandler

class FileHandler(BaseHandler):
    """
    FileHandler class is used to load configuration specific to the file handler
    """
    def __init__(self, LogLevel, LogFormat, UseLogLineStartTag, filepath):
        super().__init__(LogLevel, LogFormat, UseLogLineStartTag)

        self._filepath = filepath
        return
    
    @property
    def settings(self):
        return {
            'logLevel': self._logLevel,
            'logFormat': self._logFormat,
            'useLogLineStartTag': self._useLogLineStartTag,
            'filepath': self._filepath,
        }


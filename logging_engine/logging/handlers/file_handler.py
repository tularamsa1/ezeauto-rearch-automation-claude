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

    # def get_file_handler(self):
    #     file_handler = logging.FileHandler("execution_logs.log")
    #     file_handler.setLevel(self._file_log_level)
    #     file_handler.setFormatter(logging.Formatter(self._log_format))
    #     return file_handler

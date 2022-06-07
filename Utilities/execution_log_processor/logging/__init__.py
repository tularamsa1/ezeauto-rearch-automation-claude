
import logging

# internal imports
from ..config_utilities import Config
from .handlers.file_handler import FileHandler
from .handlers.console_handler import ConsoleHandler

from .logfile_utils import get_log_file_path


class _EzeAutoLogger(logging.getLoggerClass()):

    def __init__(self, name, level=logging.NOTSET) -> None:
        super().__init__(name, level)
        self._config = Config()
        self._assign_config_to_logger()

        self._consoleHandler = ConsoleHandler(self._consoleHandler_logLevel, self._consoleHandler_logFormat, self._consoleHandler_useLogLineStartTag)
        self._fileHandler = FileHandler(
            self._fileHandler_logLevel, self._fileHandler_logFormat, self._fileHandler_useLogLineStartTag,
            filepath = self._logFile,
        )

        self.setLevel(self._logLevel)
    
        if self._useFileHandler:
            self.addHandler(self._get_file_handler())
        if self._useConsoleHandler:
            self.addHandler(self._get_stream_handler())

        return
    
    @property
    def config(self):
        return self._config

    @property
    def logger(self):
        return self._logger

    @property
    def consoleHandler(self):
        return self._consoleHandler

    @property
    def fileHandler(self):
        return self._fileHandler

        

    def _assign_config_to_logger(self) -> None:
        '''
        Assigns the configuration to the logger
        '''
        self._logFile = get_log_file_path()
        self._logLevel = self._config.settings['logLevel']
        # print(self._logLevel)
        # self._logFile = self._config.settings['logFile']
        self._logFormat = self._config.settings['logFormat']
        self._useFileHandler = self._config.settings['useFileHandler']
        self._useConsoleHandler = self._config.settings['useConsoleHandler']
        self._useLogLineStartTag = self._config.settings['useLogLineStartTag']
        
        self._fileHandler_logLevel = self._config.settings['fileHandler']['logLevel']
        self._fileHandler_logFormat = self._config.settings['fileHandler']['logFormat']
        self._fileHandler_useLogLineStartTag = self._config.settings['fileHandler']['useLogLineStartTag']

        self._consoleHandler_logLevel = self._config.settings['consoleHandler']['logLevel']
        self._consoleHandler_logFormat = self._config.settings['consoleHandler']['logFormat']
        self._consoleHandler_useLogLineStartTag = self._config.settings['consoleHandler']['useLogLineStartTag']

        return

    def _get_file_handler(self):
        file_handler = logging.FileHandler(self._logFile)
        file_handler.setLevel(self._fileHandler_logLevel)
        file_handler.setFormatter(logging.Formatter(self._fileHandler_logFormat))
        return file_handler
    
    def _get_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self._consoleHandler_logLevel)
        stream_handler.setFormatter(logging.Formatter(self._consoleHandler_logFormat))
        return stream_handler










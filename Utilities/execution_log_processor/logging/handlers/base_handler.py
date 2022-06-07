

class BaseHandler():
    """
    BaseHandler class is used to load configuration specific to the each handler
    """
    def __init__(self, LogLevel, LogFormat, UseLogLineStartTag):
        self._logLevel = LogLevel
        self._logFormat = LogFormat
        self._useLogLineStartTag = UseLogLineStartTag


    @property
    def logLevel(self):
        return self._logLevel
    
    @property
    def logFormat(self):
        return self._logFormat

    @property
    def useLogLineStartTag(self):
        return self._useLogLineStartTag

    @property
    def settings(self):
        return {
            'logLevel': self._logLevel,
            'logFormat': self._logFormat,
            'useLogLineStartTag': self._useLogLineStartTag,
        }
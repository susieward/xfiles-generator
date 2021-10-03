
class AppException(Exception):
    def __init__(self, message: str, extras = None):
        super().__init__(message, extras)


class TextGeneratorException(AppException):
    def __init__(self, message: str, exc):
        extras = { 'exc': exc }
        super().__init__(message=message, extras=extras)


class ConnectionException(AppException):
    def __init__(self, message: str, exc):
        extras = {
            'exc': exc
        }
        super().__init__(message, extras)

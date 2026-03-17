"""
Custom exceptions for the server with HTTP status code mapping.
"""


class ServerBaseException(Exception):
    """Base exception for all server errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(ServerBaseException):
    """Raised when request parameters are invalid (HTTP 400)."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ResourceNotFoundError(ServerBaseException):
    """Raised when a requested resource is not found (HTTP 404)."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class InternalServerError(ServerBaseException):
    """Raised for internal server errors (HTTP 500)."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

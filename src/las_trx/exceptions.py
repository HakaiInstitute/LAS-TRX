"""Standardized exception handling for the application."""

import logging
from collections.abc import Callable
from typing import Any

from las_trx.logger import logger


class LASTransformError(Exception):
    """Base exception for LAS transformation operations."""
    
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize with message and optional cause.
        
        Args:
            message: Error message
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.cause = cause
    
    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class ConfigurationError(LASTransformError):
    """Exception for configuration-related errors."""
    pass


class FileOperationError(LASTransformError):
    """Base exception for file operations."""
    pass


class TransformationError(LASTransformError):
    """Exception for coordinate transformation errors."""
    pass


class UIError(LASTransformError):
    """Exception for UI-related errors."""
    pass


class NetworkError(LASTransformError):
    """Exception for network-related operations."""
    pass


def handle_exception(
    exception: Exception,
    error_type: type[LASTransformError] | None = None,
    user_message: str | None = None,
    log_level: int = logging.ERROR,
    reraise: bool = True
) -> LASTransformError | None:
    """Standardized exception handling function.
    
    Args:
        exception: The original exception
        error_type: Type of LASTransformError to wrap with (defaults to LASTransformError)
        user_message: User-friendly message (defaults to exception message)
        log_level: Logging level for the error
        reraise: Whether to reraise the wrapped exception
        
    Returns:
        Wrapped exception if reraise=False, otherwise None
        
    Raises:
        LASTransformError: Wrapped exception if reraise=True
    """
    if error_type is None:
        error_type = LASTransformError
    
    if user_message is None:
        user_message = str(exception)
    
    # Log the original exception with full traceback
    logger.log(log_level, f"Exception handled: {user_message}", exc_info=exception)
    
    # Create wrapped exception
    wrapped_exception = error_type(user_message, cause=exception)
    
    if reraise:
        raise wrapped_exception
    else:
        return wrapped_exception


def safe_execute(
    operation: Callable,
    error_type: type[LASTransformError] | None = None,
    user_message: str | None = None,
    default_return: Any = None,  # noqa: ANN401
    log_level: int = logging.ERROR
) -> Any:  # noqa: ANN401
    """Safely execute an operation with standardized error handling.
    
    Args:
        operation: Function to execute
        error_type: Type of exception to wrap with
        user_message: User-friendly error message
        default_return: Value to return if operation fails
        log_level: Logging level for errors
        
    Returns:
        Result of operation or default_return if it fails
    """
    try:
        return operation()
    except Exception as e:
        handle_exception(
            e,
            error_type=error_type,
            user_message=user_message,
            log_level=log_level,
            reraise=False
        )
        return default_return


class ExceptionContext:
    """Context manager for handling exceptions with consistent logging."""
    
    def __init__(
        self,
        error_type: type[LASTransformError] = LASTransformError,
        user_message: str | None = None,
        log_level: int = logging.ERROR,
        reraise: bool = True
    ) -> None:
        """Initialize exception context.
        
        Args:
            error_type: Type of exception to wrap with
            user_message: User-friendly error message
            log_level: Logging level
            reraise: Whether to reraise wrapped exceptions
        """
        self.error_type = error_type
        self.user_message = user_message
        self.log_level = log_level
        self.reraise = reraise
    
    def __enter__(self) -> "ExceptionContext":
        return self
    
    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> bool:  # noqa: ANN401
        if exc_type is not None:
            handle_exception(
                exc_val,
                error_type=self.error_type,
                user_message=self.user_message,
                log_level=self.log_level,
                reraise=self.reraise
            )
            return not self.reraise  # Suppress exception if not reraising
        return False
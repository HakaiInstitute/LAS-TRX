"""Application constants and configuration values."""

from enum import Enum


class UIConstants:
    """UI-related constants."""

    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 780
    PROGRESS_UPDATE_INTERVAL = 0.1  # seconds


class ProcessingConstants:
    """Data processing constants."""

    DEFAULT_CHUNK_SIZE = 10_000
    DEFAULT_SCALE_PRECISION = 0.01


class FileConstants:
    """File-related constants."""

    LAS_EXTENSIONS = ("*.las", "*.laz")
    CONFIG_EXTENSION = "*.json"
    LOG_EXTENSION = "*.log"

    # File dialog filters
    LAS_FILTER = "LAS Files (*.las *.laz)"
    CONFIG_FILTER = "Config Files (*.json)"
    LOG_FILTER = "Log Files (*.log)"


class NetworkConstants:
    """Network-related constants."""

    GITHUB_API_TIMEOUT = 10  # seconds
    GITHUB_API_HEADERS = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


class LogLevels(Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

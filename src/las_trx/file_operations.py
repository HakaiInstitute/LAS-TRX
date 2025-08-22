"""File operations with proper error handling and context management."""

import json
from pathlib import Path

from pydantic import ValidationError

from las_trx.config import TransformConfig
from las_trx.logger import logger


class FileOperationError(Exception):
    """Base exception for file operations."""
    pass


class ConfigFileError(FileOperationError):
    """Exception for configuration file operations."""
    pass


class LogFileError(FileOperationError):
    """Exception for log file operations."""
    pass


def save_config_to_file(config: TransformConfig, file_path: Path) -> None:
    """Save configuration to file with proper error handling.
    
    Args:
        config: Configuration to save
        file_path: Path to save the configuration
        
    Raises:
        ConfigFileError: If file cannot be written
    """
    try:
        logger.info(f"Saving config to {file_path}")
        with file_path.open("w", encoding="utf-8") as f:
            f.write(config.model_dump_json(indent=2))
    except OSError as e:
        error_msg = f"Failed to save config to {file_path}: {e}"
        logger.error(error_msg)
        raise ConfigFileError(error_msg) from e


def load_config_from_file(file_path: Path) -> TransformConfig:
    """Load configuration from file with proper error handling.
    
    Args:
        file_path: Path to load configuration from
        
    Returns:
        Loaded configuration
        
    Raises:
        ConfigFileError: If file cannot be read or parsed
    """
    try:
        logger.info(f"Loading config from {file_path}")
        with file_path.open("r", encoding="utf-8") as f:
            config_data = f.read()
            
        return TransformConfig.model_validate_json(config_data)
        
    except OSError as e:
        error_msg = f"Failed to read config file {file_path}: {e}"
        logger.error(error_msg)
        raise ConfigFileError(error_msg) from e
    except (json.JSONDecodeError, ValidationError) as e:
        error_msg = f"Invalid config file format in {file_path}: {e}"
        logger.error(error_msg)
        raise ConfigFileError(error_msg) from e


def export_logs_to_file(log_content: str, file_path: Path) -> None:
    """Export logs to file with proper error handling.
    
    Args:
        log_content: Log content to save
        file_path: Path to save the logs
        
    Raises:
        LogFileError: If file cannot be written
    """
    try:
        logger.info(f"Exporting logs to {file_path}")
        with file_path.open("w", encoding="utf-8") as f:
            f.write(log_content)
    except OSError as e:
        error_msg = f"Failed to save logs to {file_path}: {e}"
        logger.error(error_msg)
        raise LogFileError(error_msg) from e


def validate_file_paths(input_files: list[Path], output_files: list[Path]) -> None:
    """Validate input and output file paths for conflicts.
    
    Args:
        input_files: List of input file paths
        output_files: List of output file paths
        
    Raises:
        FileOperationError: If validation fails
    """
    # Check for input/output file conflicts
    for input_file in input_files:
        if input_file in output_files:
            raise FileOperationError(
                "One of input files matches name of output files. "
                "Aborting because this would overwrite that input file."
            )
    
    # Check for duplicate output files
    if len(output_files) != len(set(output_files)):
        raise FileOperationError(
            "Duplicate output file name detected. "
            "Use a format string for the output path to output a file based on the "
            "stem of the corresponding input file. "
            r"e.g. 'C:\\some\path\{}_nad83csrs.laz'"
        )


def ensure_output_extension(output_file: Path, default_extension: str = ".laz") -> Path:
    """Ensure output file has proper extension.
    
    Args:
        output_file: Output file path
        default_extension: Default extension to add if missing
        
    Returns:
        Path with proper extension
    """
    if not output_file.suffix:
        return output_file.with_suffix(default_extension)
    return output_file
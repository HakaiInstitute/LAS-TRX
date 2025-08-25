"""UI Controllers for separating business logic from UI code."""

import os
from datetime import date
from pathlib import Path
from typing import Protocol

from loguru import logger
from PyQt6.QtWidgets import QComboBox, QFileDialog, QWidget

from las_trx.config import ReferenceConfig, TransformConfig, TrxCoordType, TrxReference, TrxVd
from las_trx.constants import FileConstants
from las_trx.file_operations import (
    ConfigFileError,
    LogFileError,
    export_logs_to_file,
    load_config_from_file,
    save_config_to_file,
)


class UIWidgetAccess(Protocol):
    """Protocol for accessing UI widgets in a type-safe way."""

    def get_input_file_path(self) -> str: ...
    def set_input_file_path(self, path: str) -> None: ...
    def get_output_file_path(self) -> str: ...
    def set_output_file_path(self, path: str) -> None: ...
    def get_log_content(self) -> str: ...
    def show_error_message(self, message: str) -> None: ...
    def show_success_message(self, message: str) -> None: ...


class FileController:
    """Controller for file operations."""

    def __init__(self, parent: QWidget, ui_access: UIWidgetAccess) -> None:
        self.parent = parent
        self.ui_access = ui_access
        self.dialog_directory = Path("~").expanduser()

    def select_input_file(self) -> None:
        """Handle input file selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Select input LAS file",
            directory=self.dialog_directory,
            filter=FileConstants.LAS_FILTER,
        )
        if file_path:
            self.ui_access.set_input_file_path(file_path)
            self.dialog_directory = Path(file_path).parent

    def select_output_file(self) -> None:
        """Handle output file selection."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Select output LAS file",
            directory=self.dialog_directory,
            filter=FileConstants.LAS_FILTER,
        )
        if file_path:
            self.ui_access.set_output_file_path(file_path)
            self.dialog_directory = Path(file_path).parent

    def save_config(self, config: TransformConfig) -> None:
        """Save configuration to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save Config",
            directory=self.dialog_directory,
            filter=FileConstants.CONFIG_FILTER,
        )
        if file_path:
            try:
                save_config_to_file(config, Path(file_path))
                self.ui_access.show_success_message("Configuration saved successfully")
            except ConfigFileError as e:
                self.ui_access.show_error_message(str(e))

    def load_config(self) -> TransformConfig | None:
        """Load configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Load Config",
            directory=self.dialog_directory,
            filter=FileConstants.CONFIG_FILTER,
        )
        if file_path:
            try:
                return load_config_from_file(Path(file_path))
            except ConfigFileError as e:
                self.ui_access.show_error_message(str(e))
                return None
        return None

    def export_logs(self) -> None:
        """Export logs to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Export Logs",
            directory=self.dialog_directory,
            filter=FileConstants.LOG_FILTER,
        )
        if file_path:
            try:
                log_content = self.ui_access.get_log_content()
                export_logs_to_file(log_content, Path(file_path))
                self.ui_access.show_success_message("Logs exported successfully")
            except LogFileError as e:
                self.ui_access.show_error_message(str(e))


class ConfigurationController:
    """Controller for configuration management."""

    @staticmethod
    def update_vertical_datum_options(reference_text: str, combo_box: QComboBox) -> None:
        """Update vertical datum options based on reference frame."""
        combo_box.clear()
        if reference_text == "NAD83(CSRS)":
            combo_box.addItems(["GRS80", "CGVD2013/CGG2013a", "CGVD2013/CGG2013", "CGVD28/HT2_2010v70"])
        elif reference_text == "WGS84":
            combo_box.addItems(["WGS84"])
        else:
            combo_box.addItems(["GRS80"])

    @staticmethod
    def create_reference_config(
        ref_frame: TrxReference, epoch: date, vd: TrxVd, coord_type: TrxCoordType
    ) -> ReferenceConfig:
        """Create a reference configuration."""
        return ReferenceConfig(
            ref_frame=ref_frame,
            epoch=epoch,
            vd=vd,
            coord_type=coord_type,
        )

    @staticmethod
    def create_transform_config(
        origin: ReferenceConfig, destination: ReferenceConfig, max_workers: int
    ) -> TransformConfig:
        """Create a transformation configuration."""
        return TransformConfig(origin=origin, destination=destination, max_workers=max_workers)

    @staticmethod
    def validate_core_count(value: int) -> int:
        """Validate and correct core count value."""
        max_cores = os.cpu_count() or 1
        if value > max_cores:
            logger.warning(f"Core count {value} exceeds maximum {max_cores}, using {max_cores}")
            return max_cores
        elif value < 1:
            logger.warning(f"Core count {value} below minimum 1, using 1")
            return 1
        return value


class TransformationController:
    """Controller for coordinate transformation operations."""

    def __init__(self, ui_access: UIWidgetAccess) -> None:
        self.ui_access = ui_access
        self.worker_thread: object | None = None  # Will be TransformWorker

    def start_transformation(self, config: TransformConfig, input_pattern: str, output_pattern: str) -> None:
        """Start coordinate transformation process."""
        # This will be implemented when we refactor the worker
        logger.debug("Starting transformation process")
        # TODO: Implement after worker refactoring

    def stop_transformation(self) -> None:
        """Stop ongoing transformation process."""
        if self.worker_thread:
            # TODO: Implement proper cleanup
            logger.debug("Stopping transformation process")

    def on_transformation_success(self) -> None:
        """Handle successful transformation completion."""
        logger.info("Processing complete")
        self.ui_access.show_success_message("File(s) converted successfully")

    def on_transformation_error(self, error: Exception) -> None:
        """Handle transformation error."""
        logger.error(f"Transformation error: {error}")
        self.ui_access.show_error_message(str(error))

"""UI abstraction layer to decouple business logic from direct widget access."""

from collections.abc import Callable
from datetime import date
from typing import Protocol, runtime_checkable

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QComboBox, QWidget

from las_trx.config import TrxCoordType, TrxReference, TrxVd


@runtime_checkable
class UIWidgetInterface(Protocol):
    """Protocol defining the interface for UI widget access."""

    # File paths
    def get_input_file_path(self) -> str: ...
    def set_input_file_path(self, path: str) -> None: ...
    def get_output_file_path(self) -> str: ...
    def set_output_file_path(self, path: str) -> None: ...

    # Reference frames
    def get_input_reference(self) -> TrxReference: ...
    def set_input_reference(self, reference: TrxReference) -> None: ...
    def get_output_reference(self) -> TrxReference: ...
    def set_output_reference(self, reference: TrxReference) -> None: ...

    # Epochs
    def get_input_epoch(self) -> date: ...
    def set_input_epoch(self, epoch: date) -> None: ...
    def get_output_epoch(self) -> date: ...
    def set_output_epoch(self, epoch: date) -> None: ...
    def is_epoch_transformation_enabled(self) -> bool: ...
    def set_epoch_transformation_enabled(self, enabled: bool) -> None: ...

    # Vertical datums
    def get_input_vertical_datum(self) -> TrxVd: ...
    def set_input_vertical_datum(self, vd: TrxVd) -> None: ...
    def get_output_vertical_datum(self) -> TrxVd: ...
    def set_output_vertical_datum(self, vd: TrxVd) -> None: ...
    def get_input_vd_combobox(self) -> QComboBox: ...
    def get_output_vd_combobox(self) -> QComboBox: ...

    # Coordinate types
    def get_input_coordinate_type(self) -> TrxCoordType: ...
    def set_input_coordinate_type(self, coord_type: TrxCoordType) -> None: ...
    def get_output_coordinate_type(self) -> TrxCoordType: ...
    def set_output_coordinate_type(self, coord_type: TrxCoordType) -> None: ...
    def get_input_utm_zone(self) -> int: ...
    def set_input_utm_zone(self, zone: int) -> None: ...
    def get_output_utm_zone(self) -> int: ...
    def set_output_utm_zone(self, zone: int) -> None: ...
    def set_input_utm_zone_enabled(self, enabled: bool) -> None: ...
    def set_output_utm_zone_enabled(self, enabled: bool) -> None: ...

    # Worker settings
    def get_worker_cores(self) -> int: ...
    def set_worker_cores(self, cores: int) -> None: ...

    # Progress and status
    def set_progress(self, value: int) -> None: ...
    def set_convert_button_enabled(self, enabled: bool) -> None: ...

    # Log output
    def get_log_content(self) -> str: ...
    def append_log_text(self, text: str) -> None: ...

    # Messages
    def show_success_message(self, message: str) -> None: ...
    def show_error_message(self, message: str) -> None: ...


class UIWidgetAdapter:
    """Adapter that implements UIWidgetInterface for the main window's central widget."""

    def __init__(self, central_widget: QWidget) -> None:
        """Initialize with the main window's central widget.

        Args:
            central_widget: The central widget containing all UI elements
        """
        self.cw = central_widget
        self._success_callback = None
        self._error_callback = None

    def set_message_callbacks(
        self, success_callback: Callable[[str], None], error_callback: Callable[[str], None]
    ) -> None:
        """Set callbacks for success and error messages."""
        self._success_callback = success_callback
        self._error_callback = error_callback

    # File paths
    def get_input_file_path(self) -> str:
        return self.cw.lineEdit_input_file.text()

    def set_input_file_path(self, path: str) -> None:
        self.cw.lineEdit_input_file.setText(path)

    def get_output_file_path(self) -> str:
        return self.cw.lineEdit_output_file.text()

    def set_output_file_path(self, path: str) -> None:
        self.cw.lineEdit_output_file.setText(path)

    # Reference frames
    def get_input_reference(self) -> TrxReference:
        return TrxReference(self.cw.comboBox_input_reference.currentText())

    def set_input_reference(self, reference: TrxReference) -> None:
        self.cw.comboBox_input_reference.setCurrentText(reference.value)

    def get_output_reference(self) -> TrxReference:
        return TrxReference(self.cw.comboBox_output_reference.currentText())

    def set_output_reference(self, reference: TrxReference) -> None:
        self.cw.comboBox_output_reference.setCurrentText(reference.value)

    # Epochs
    def get_input_epoch(self) -> date:
        return self.cw.dateEdit_input_epoch.date().toPyDate()

    def set_input_epoch(self, epoch: date) -> None:
        self.cw.dateEdit_input_epoch.setDate(QDate(epoch))

    def get_output_epoch(self) -> date:
        if self.is_epoch_transformation_enabled():
            return self.cw.dateEdit_output_epoch.date().toPyDate()
        else:
            return self.get_input_epoch()

    def set_output_epoch(self, epoch: date) -> None:
        self.cw.dateEdit_output_epoch.setDate(QDate(epoch))

    def is_epoch_transformation_enabled(self) -> bool:
        return self.cw.checkBox_epoch_trans.isChecked()

    def set_epoch_transformation_enabled(self, enabled: bool) -> None:
        self.cw.checkBox_epoch_trans.setChecked(enabled)
        self.cw.dateEdit_output_epoch.setEnabled(enabled)
        if not enabled:
            self.set_output_epoch(self.get_input_epoch())

    # Vertical datums
    def get_input_vertical_datum(self) -> TrxVd:
        return TrxVd(self.cw.comboBox_input_vertical_reference.currentText())

    def set_input_vertical_datum(self, vd: TrxVd) -> None:
        self.cw.comboBox_input_vertical_reference.setCurrentText(vd.value)

    def get_output_vertical_datum(self) -> TrxVd:
        return TrxVd(self.cw.comboBox_output_vertical_reference.currentText())

    def set_output_vertical_datum(self, vd: TrxVd) -> None:
        self.cw.comboBox_output_vertical_reference.setCurrentText(vd.value)

    def get_input_vd_combobox(self) -> QComboBox:
        return self.cw.comboBox_input_vertical_reference

    def get_output_vd_combobox(self) -> QComboBox:
        return self.cw.comboBox_output_vertical_reference

    # Coordinate types
    def get_input_coordinate_type(self) -> TrxCoordType:
        coord_text = self.cw.comboBox_input_coordinates.currentText()
        if coord_text == "UTM":
            return TrxCoordType.from_utm_zone(self.get_input_utm_zone())
        return TrxCoordType(coord_text)

    def set_input_coordinate_type(self, coord_type: TrxCoordType) -> None:
        if coord_type.is_utm():
            self.cw.comboBox_input_coordinates.setCurrentText("UTM")
            self.set_input_utm_zone(coord_type.utm_zone)
        else:
            self.cw.comboBox_input_coordinates.setCurrentText(coord_type.value)

    def get_output_coordinate_type(self) -> TrxCoordType:
        coord_text = self.cw.comboBox_output_coordinates.currentText()
        if coord_text == "UTM":
            return TrxCoordType.from_utm_zone(self.get_output_utm_zone())
        return TrxCoordType(coord_text)

    def set_output_coordinate_type(self, coord_type: TrxCoordType) -> None:
        if coord_type.is_utm():
            self.cw.comboBox_output_coordinates.setCurrentText("UTM")
            self.set_output_utm_zone(coord_type.utm_zone)
        else:
            self.cw.comboBox_output_coordinates.setCurrentText(coord_type.value)

    def get_input_utm_zone(self) -> int:
        return self.cw.spinBox_input_utm_zone.value()

    def set_input_utm_zone(self, zone: int) -> None:
        self.cw.spinBox_input_utm_zone.setValue(zone)

    def get_output_utm_zone(self) -> int:
        return self.cw.spinBox_output_utm_zone.value()

    def set_output_utm_zone(self, zone: int) -> None:
        self.cw.spinBox_output_utm_zone.setValue(zone)

    def set_input_utm_zone_enabled(self, enabled: bool) -> None:
        self.cw.spinBox_input_utm_zone.setEnabled(enabled)

    def set_output_utm_zone_enabled(self, enabled: bool) -> None:
        self.cw.spinBox_output_utm_zone.setEnabled(enabled)

    # Worker settings
    def get_worker_cores(self) -> int:
        return self.cw.spinBox_worker_cores.value()

    def set_worker_cores(self, cores: int) -> None:
        self.cw.spinBox_worker_cores.setValue(cores)

    # Progress and status
    def set_progress(self, value: int) -> None:
        self.cw.progressBar.setValue(value)

    def set_convert_button_enabled(self, enabled: bool) -> None:
        self.cw.pushButton_convert.setEnabled(enabled)

    # Log output
    def get_log_content(self) -> str:
        return self.cw.textBrowser_log_output.toPlainText()

    def append_log_text(self, text: str) -> None:
        self.cw.textBrowser_log_output.append(text)

    # Messages
    def show_success_message(self, message: str) -> None:
        if self._success_callback:
            self._success_callback(message)

    def show_error_message(self, message: str) -> None:
        if self._error_callback:
            self._error_callback(message)

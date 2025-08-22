"""Modern main window implementation using improved components."""

import os
import queue
from datetime import date
from queue import Queue

from csrspy.utils import sync_missing_grid_files
from loguru import logger
from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSignal as Signal
from PyQt6.QtGui import QCloseEvent, QIcon, QKeySequence, QTextCursor
from PyQt6.QtWidgets import (
    QErrorMessage,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QWidget,
)

from las_trx import __version__
from las_trx.config import TrxReference, TrxVd
from las_trx.config_builder import ConfigurationBuilder
from las_trx.constants import UIConstants
from las_trx.controllers import ConfigurationController, FileController
from las_trx.ui_interface import UIWidgetAdapter
from las_trx.utils import get_upgrade_version, resource_path
from las_trx.widgets import WidgetFactory
from las_trx.worker import TransformWorker


class MainWindow(QMainWindow):
    """Modern main window using improved architecture."""

    def __init__(self) -> None:
        super().__init__()

        # Initialize UI
        self._setup_window()
        self._setup_central_widget()
        self._setup_dialogs()
        self._setup_menu_bar()

        # Initialize new architecture components
        self._setup_ui_interface()
        self._setup_controllers()
        self._setup_worker_spinbox()
        self._setup_platform_specific_styling()

        # Connect signals
        self._connect_signals()

        # Initialize debug mode if enabled
        if os.getenv("DEBUG"):
            self._setup_debug_mode()

        # Sync grid files
        sync_missing_grid_files()

        # Current worker thread
        self.current_worker: TransformWorker | None = None

    def _setup_window(self) -> None:
        """Setup main window properties."""
        self.setWindowIcon(QIcon(resource_path("resources/las-trx.ico")))
        self.setWindowTitle(f"LAS TRX v{__version__}")

        # Set window size using constants
        rect = self.frameGeometry()
        rect.setWidth(UIConstants.DEFAULT_WINDOW_WIDTH)
        rect.setHeight(UIConstants.DEFAULT_WINDOW_HEIGHT)
        self.setProperty("geometry", rect)

    def _setup_central_widget(self) -> None:
        """Setup central widget and load UI."""
        self.cw = QWidget()
        self.setCentralWidget(self.cw)
        uic.loadUi(resource_path("resources/mainwindow.ui"), self.cw)

        # Check for upgrade
        self._check_for_upgrade()

    def _setup_dialogs(self) -> None:
        """Setup dialog boxes."""
        self.success_msg_box = QMessageBox(self)
        self.success_msg_box.setWindowTitle("Success")

        self.error_msg_box = QErrorMessage(self)
        self.error_msg_box.setWindowTitle("Error")

        self.help_msg_box = QMessageBox(self)
        self.help_msg_box.setText(
            "<h3>Batch Processing</h3>"
            "<p>Use '*' in the input file to select multiple files, <i>e.g.</i>"
            "<pre>C:\\\\path\\to\\files\\*.laz</pre>"
            "<p>Use '{}' in the output file to generate a name from the input name, <i>e.g.</i></p>"
            "<pre>C:\\\\path\\to\\files\\{}_nad83.laz</pre>"
        )
        self.help_msg_box.setWindowTitle("Help")

    def _setup_menu_bar(self) -> None:
        """Setup menu bar with actions."""
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # File menu
        file_menu = QMenu("File", self)
        self.menu_bar.addMenu(file_menu)

        export_log_action = file_menu.addAction("Export Logs")
        export_log_action.triggered.connect(self._export_logs)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)

        # Config menu
        config_menu = QMenu("Config", self)
        self.menu_bar.addMenu(config_menu)

        save_config_action = config_menu.addAction("Save")
        save_config_action.setShortcut(QKeySequence.StandardKey.Save)
        save_config_action.triggered.connect(self._save_config)

        load_config_action = config_menu.addAction("Load")
        load_config_action.setShortcut(QKeySequence.StandardKey.Open)
        load_config_action.triggered.connect(self._load_config)

        # Help menu
        help_menu = QMenu("Help", self)
        self.menu_bar.addMenu(help_menu)

        batch_mode_action = help_menu.addAction("Batch Processing")
        batch_mode_action.triggered.connect(self.help_msg_box.exec)

    def _setup_ui_interface(self) -> None:
        """Setup UI abstraction layer."""
        self.ui_adapter = UIWidgetAdapter(self.cw)
        self.ui_adapter.set_message_callbacks(
            success_callback=self._show_success_message, error_callback=self._show_error_message
        )

    def _setup_controllers(self) -> None:
        """Setup controller components."""
        self.file_controller = FileController(self, self.ui_adapter)
        self.config_controller = ConfigurationController()
        self.config_builder = ConfigurationBuilder(self.ui_adapter)

    def _setup_worker_spinbox(self) -> None:
        """Replace standard spinbox with custom worker cores spinbox."""
        old_spinbox = self.cw.spinBox_worker_cores
        new_spinbox = WidgetFactory.create_worker_cores_spinbox()

        # Replace widget in layout
        if WidgetFactory.replace_widget_in_layout(old_spinbox, new_spinbox):
            self.cw.spinBox_worker_cores = new_spinbox
            new_spinbox.valueChanged.connect(self._validate_core_count)
        else:
            logger.warning("Failed to replace worker cores spinbox")

    def _setup_platform_specific_styling(self) -> None:
        """Apply platform-specific styling fixes."""
        import platform

        if platform.system() == "Windows":
            # Windows-specific styling for UTM zone spinboxes
            utm_spinbox_style = """
                QSpinBox {
                    border: 1px solid black;
                    padding-right: 15px;
                }
                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 15px;
                }
                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 15px;
                }
            """
            self.cw.spinBox_input_utm_zone.setStyleSheet(utm_spinbox_style)
            self.cw.spinBox_output_utm_zone.setStyleSheet(utm_spinbox_style)

    def _connect_signals(self) -> None:
        """Connect UI signals to handlers."""
        # File selection
        self.cw.toolButton_input_file.clicked.connect(self.file_controller.select_input_file)
        self.cw.toolButton_output_file.clicked.connect(self.file_controller.select_output_file)

        # Configuration changes
        self.cw.checkBox_epoch_trans.clicked.connect(self._enable_epoch_transformation)
        self.cw.comboBox_input_reference.currentTextChanged.connect(
            lambda text: self.config_controller.update_vertical_datum_options(
                text, self.ui_adapter.get_input_vd_combobox()
            )
        )
        self.cw.comboBox_output_reference.currentTextChanged.connect(
            lambda text: self.config_controller.update_vertical_datum_options(
                text, self.ui_adapter.get_output_vd_combobox()
            )
        )
        self.cw.dateEdit_input_epoch.dateChanged.connect(self._maybe_update_output_epoch)

        # Coordinate type changes
        self.cw.comboBox_input_coordinates.currentTextChanged.connect(
            lambda text: self.ui_adapter.set_input_utm_zone_enabled(text == "UTM")
        )
        self.cw.comboBox_output_coordinates.currentTextChanged.connect(
            lambda text: self.ui_adapter.set_output_utm_zone_enabled(text == "UTM")
        )

        # Help and conversion
        self.cw.toolButton_help.clicked.connect(self.help_msg_box.exec)
        self.cw.pushButton_convert.clicked.connect(self._start_conversion)

    def _check_for_upgrade(self) -> None:
        """Check for available upgrades."""
        upgrade_version = get_upgrade_version(__version__)
        if upgrade_version is None:
            self.cw.label_upgrade_link.hide()
        else:
            self.cw.label_upgrade_link.setText(
                f'<a href="{upgrade_version["html_url"]}">'
                '<span style="text-decoration: underline; color:rgb(153, 193, 241)">'
                f"New version available (v{upgrade_version['tag_name']})"
                f"</span></a>"
            )

    def _setup_debug_mode(self) -> None:
        """Setup debug mode with test values."""
        self.ui_adapter.set_input_file_path("/home/taylor/PycharmProjects/Las-TRX/testfiles/20_3028_01/*.laz")
        self.ui_adapter.set_input_reference(TrxReference.ITRF14)
        self.ui_adapter.set_input_epoch(date(2020, 8, 12))

        self.ui_adapter.set_output_file_path(
            "/home/taylor/PycharmProjects/Las-TRX/testfiles/20_3028_01_converted/{}.laz"
        )
        self.ui_adapter.set_epoch_transformation_enabled(True)
        self.ui_adapter.set_output_epoch(date(2002, 1, 1))
        self.ui_adapter.set_output_vertical_datum(TrxVd.CGG2013A)

    def _validate_core_count(self, value: int) -> None:
        """Validate and correct core count."""
        corrected_value = self.config_controller.validate_core_count(value)
        if corrected_value != value:
            self.ui_adapter.set_worker_cores(corrected_value)

    def _enable_epoch_transformation(self, checked: bool) -> None:
        """Enable/disable epoch transformation."""
        self.ui_adapter.set_epoch_transformation_enabled(checked)

    def _maybe_update_output_epoch(self, new_date: date) -> None:
        """Update output epoch if epoch transformation is disabled."""
        if not self.ui_adapter.is_epoch_transformation_enabled():
            self.ui_adapter.set_output_epoch(new_date)

    def _save_config(self) -> None:
        """Save current configuration."""
        try:
            config = self.config_builder.build_transform_config()
            self.file_controller.save_config(config)
        except Exception as e:
            self._show_error_message(f"Failed to save configuration: {e}")

    def _load_config(self) -> None:
        """Load configuration from file."""
        config = self.file_controller.load_config()
        if config:
            self.config_builder.apply_config_to_ui(config)

    def _export_logs(self) -> None:
        """Export logs to file."""
        self.file_controller.export_logs()

    def _start_conversion(self) -> None:
        """Start coordinate transformation."""
        try:
            # Build configuration
            config = self.config_builder.build_transform_config()

            # Validate configuration
            issues = self.config_builder.validate_configuration(config)
            if issues:
                self._show_error_message("Configuration issues:\\n" + "\\n".join(issues))
                return

            # Get file patterns
            input_pattern = self.ui_adapter.get_input_file_path()
            output_pattern = self.ui_adapter.get_output_file_path()

            # Stop any existing worker
            if self.current_worker and self.current_worker.isRunning():
                self.current_worker.stop_transformation()
                self.current_worker.wait()

            # Create and start new worker
            self.current_worker = TransformWorker(
                config=config, input_pattern=input_pattern, output_pattern=output_pattern, parent=self
            )

            # Connect worker signals
            self.current_worker.progress.connect(self.ui_adapter.set_progress)
            self.current_worker.success.connect(self._on_conversion_success)
            self.current_worker.error.connect(self._on_conversion_error)
            self.current_worker.started.connect(lambda: self.ui_adapter.set_convert_button_enabled(False))
            self.current_worker.finished.connect(self._on_conversion_finished)
            self.current_worker.file_completed.connect(self._on_file_completed)

            # Start transformation
            self.current_worker.start()

        except Exception as e:
            self._show_error_message(f"Failed to start conversion: {e}")

    def _on_conversion_success(self) -> None:
        """Handle successful conversion completion."""
        self._show_success_message("File(s) converted successfully")

    def _on_conversion_error(self, error: Exception) -> None:
        """Handle conversion error."""
        self._show_error_message(f"Conversion failed: {error}")

    def _on_conversion_finished(self) -> None:
        """Handle conversion completion (success or failure)."""
        self.ui_adapter.set_convert_button_enabled(True)
        self.ui_adapter.set_progress(0)

    def _on_file_completed(self, input_file: str, output_file: str) -> None:
        """Handle individual file completion."""
        logger.info(f"Completed: {input_file} -> {output_file}")

    def _show_success_message(self, message: str) -> None:
        """Show success message dialog."""
        self.success_msg_box.setText(message)
        self.success_msg_box.exec()

    def _show_error_message(self, message: str) -> None:
        """Show error message dialog."""
        self.error_msg_box.showMessage(message)
        self.error_msg_box.exec()

    def append_text(self, text: str) -> None:
        """Append text to log output (for LogDisplayThread compatibility)."""
        self.cw.textBrowser_log_output.moveCursor(QTextCursor.MoveOperation.End)
        self.cw.textBrowser_log_output.insertPlainText(text)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle window close event."""
        # Stop any running worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop_transformation()
            self.current_worker.wait(5000)  # Wait up to 5 seconds

        super().closeEvent(event)


class LogWriteStream:
    """Stream for writing log messages to queue."""

    def __init__(self, queue_: Queue) -> None:
        super().__init__()
        self.queue = queue_

    def write(self, text: str) -> None:
        """Write text to queue."""
        self.queue.put(text)


class LogDisplayThread(QThread):
    """Thread for displaying log messages from queue."""

    on_msg = Signal(str)

    def __init__(self, queue_: Queue, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.queue = queue_

    def run(self) -> None:
        """Run the log display loop."""
        while not self.isInterruptionRequested():
            try:
                text = self.queue.get(block=False)
                self.on_msg.emit(text)
            except queue.Empty:
                continue

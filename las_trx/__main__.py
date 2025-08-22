import logging
import os.path
import queue
import sys
from datetime import date
from multiprocessing import freeze_support
from queue import Queue

from csrspy.utils import sync_missing_grid_files
from pydantic import ValidationError
from PyQt6 import uic
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QIcon, QKeySequence, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QErrorMessage,
    QFileDialog,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QWidget,
)

from las_trx import __version__
from las_trx.config import (
    ReferenceConfig,
    TransformConfig,
    TrxCoordType,
    TrxReference,
    TrxVd,
)
from las_trx.logger import logger
from las_trx.utils import get_upgrade_version, resource_path
from las_trx.worker import TransformWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window size
        rect = self.frameGeometry()
        rect.setWidth(600)
        rect.setHeight(780)
        self.setProperty("geometry", rect)

        # Load UI
        self.cw = QWidget()
        self.setCentralWidget(self.cw)
        uic.loadUi(resource_path("resources/mainwindow.ui"), self.cw)

        # Create Dialogs
        self.done_msg_box = QMessageBox(self)
        self.done_msg_box.setText("File(s) converted successfully")
        self.done_msg_box.setWindowTitle("Success")
        self.err_msg_box = QErrorMessage(self)
        self.err_msg_box.setWindowTitle("Error")
        self.help_msg_box = QMessageBox(self)
        self.help_msg_box.setText(
            "<h3>Batch Processing</h3>"
            "<p>Use '*' in the input file to select multiple files, <i>e.g.</i>"
            "<pre>C:\\\\path\\to\\files\\*.laz</pre>"
            "<p>Use '{}' in the output file to generate a name from the input name, <i>e.g.</i></p>"
            "<pre>C:\\\\path\\to\\files\\{}_nad83.laz</pre>"
        )
        self.help_msg_box.setWindowTitle("Help")

        # Setup window
        self.setWindowIcon(QIcon(resource_path("resources/las-trx.ico")))
        self.setWindowTitle(f"LAS TRX v{__version__}")

        # Create menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create File menu
        file_menu = QMenu("File", self)
        self.menu_bar.addMenu(file_menu)
        export_log_action = file_menu.addAction("Export Logs")
        export_log_action.triggered.connect(self.export_logs)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)

        # Create Config menu
        config_menu = QMenu("Config", self)
        self.menu_bar.addMenu(config_menu)
        save_config_action = config_menu.addAction("Save")
        save_config_action.setShortcut(QKeySequence.StandardKey.Save)
        save_config_action.triggered.connect(self.save_config)
        load_config_action = config_menu.addAction("Load")
        load_config_action.setShortcut(QKeySequence.StandardKey.Open)
        load_config_action.triggered.connect(self.load_config)

        # Create Help menu
        help_menu = QMenu("Help", self)
        self.menu_bar.addMenu(help_menu)
        batch_mode_action = help_menu.addAction("Batch Processing")
        batch_mode_action.triggered.connect(self.help_msg_box.exec)

        # Check for updates
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

        # Connect signals
        self.cw.toolButton_input_file.clicked.connect(self.handle_select_input_file)
        self.cw.toolButton_output_file.clicked.connect(self.handle_select_output_file)
        self.cw.checkBox_epoch_trans.clicked.connect(self.enable_epoch_trans)
        self.cw.pushButton_convert.clicked.connect(self.convert)
        self.cw.comboBox_input_reference.currentTextChanged.connect(self.update_input_vd_options)
        self.cw.comboBox_output_reference.currentTextChanged.connect(self.update_output_vd_options)
        self.cw.dateEdit_input_epoch.dateChanged.connect(self.maybe_update_output_epoch)
        self.cw.comboBox_output_coordinates.currentTextChanged.connect(self.activate_output_utm_zone_picker)
        self.cw.comboBox_input_coordinates.currentTextChanged.connect(self.activate_input_utm_zone_picker)
        self.cw.toolButton_help.clicked.connect(self.help_msg_box.exec)
        self.cw.toolButton_halve_cores.clicked.connect(self.halve_cores)
        self.cw.toolButton_double_cores.clicked.connect(self.double_cores)
        self.cw.spinBox_worker_cores.valueChanged.connect(self.validate_core_count)

        self.dialog_directory = os.path.expanduser("~")

        self.thread = None
        
        # Initialize worker cores spinbox
        max_cores = os.cpu_count()
        self.cw.spinBox_worker_cores.setMaximum(max_cores)
        self.cw.spinBox_worker_cores.setValue(max_cores)

        sync_missing_grid_files()

    def save_config(self):
        # Get output file path
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Config",
            directory=self.dialog_directory,
            filter="Config Files (*.json)",
        )
        if path:
            # Save config to file
            logger.info(f"Saving config to {path}")
            with open(path, "w") as f:
                f.write(self.transform_config.model_dump_json(indent=2))

    def load_config(self):
        # Get config file path
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Config",
            directory=self.dialog_directory,
            filter="Config Files (*.json)",
        )
        if path:
            # Load config from file
            logger.info(f"Loading config from {path}")
            with open(path) as f:
                config = f.read()
                try:
                    self.transform_config = TransformConfig.model_validate_json(config)
                except ValidationError as e:
                    logger.error(e)
                    self.err_msg_box.showMessage(str(e))
                    self.err_msg_box.exec()

    def export_logs(self):
        # Get output file path
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            directory=self.dialog_directory,
            filter="Log Files (*.log)",
        )
        if path:
            # Save logs to file
            logger.info(f"Exporting logs to {path}")
            with open(path, "w") as f:
                f.write(self.cw.textBrowser_log_output.toPlainText())

    def maybe_update_output_epoch(self, new_date: date):
        if not self.cw.checkBox_epoch_trans.isChecked():
            self.cw.dateEdit_output_epoch.setDate(new_date)

    def handle_select_input_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input LAS file",
            directory=self.dialog_directory,
            filter="LAS Files (*.las *.laz)",
        )
        if path:
            self.cw.lineEdit_input_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def handle_select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select output LAS file",
            directory=self.dialog_directory,
            filter="LAS Files (*.las *.laz)",
        )
        if path:
            self.cw.lineEdit_output_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def enable_epoch_trans(self, checked):
        self.cw.dateEdit_output_epoch.setEnabled(checked)

        if not checked:
            self.cw.dateEdit_output_epoch.setDate(self.cw.dateEdit_input_epoch.date())

    def activate_input_utm_zone_picker(self, text):
        self.cw.spinBox_input_utm_zone.setEnabled(text == "UTM")

    def activate_output_utm_zone_picker(self, text):
        self.cw.spinBox_output_utm_zone.setEnabled(text == "UTM")

    def halve_cores(self):
        current_value = self.cw.spinBox_worker_cores.value()
        new_value = max(1, current_value // 2)
        self.cw.spinBox_worker_cores.setValue(new_value)

    def double_cores(self):
        current_value = self.cw.spinBox_worker_cores.value()
        max_cores = os.cpu_count()
        new_value = min(max_cores, current_value * 2)
        self.cw.spinBox_worker_cores.setValue(new_value)

    def validate_core_count(self, value):
        max_cores = os.cpu_count()
        if value > max_cores:
            self.cw.spinBox_worker_cores.setValue(max_cores)
        elif value < 1:
            self.cw.spinBox_worker_cores.setValue(1)

    @staticmethod
    def update_vd_options(text, combo_box):
        combo_box.clear()
        if text == "NAD83(CSRS)":
            combo_box.addItems(["GRS80", "CGVD2013/CGG2013a", "CGVD2013/CGG2013", "CGVD28/HT2_2010v70"])
        elif text == "WGS84":
            combo_box.addItems(["WGS84"])
        else:
            combo_box.addItems(["GRS80"])

    def update_input_vd_options(self, text):
        self.update_vd_options(text, self.cw.comboBox_input_vertical_reference)

    def update_output_vd_options(self, text):
        self.update_vd_options(text, self.cw.comboBox_output_vertical_reference)

    @property
    def s_ref_frame(self) -> TrxReference:
        return TrxReference(self.cw.comboBox_input_reference.currentText())

    @property
    def t_ref_frame(self) -> TrxReference:
        return TrxReference(self.cw.comboBox_output_reference.currentText())

    @property
    def s_epoch(self) -> date:
        return self.cw.dateEdit_input_epoch.date().toPyDate()

    @property
    def t_epoch(self) -> date:
        if self.cw.checkBox_epoch_trans.isChecked():
            return self.cw.dateEdit_output_epoch.date().toPyDate()
        else:
            return self.s_epoch

    @property
    def s_coords(self) -> TrxCoordType:
        out_type = self.cw.comboBox_input_coordinates.currentText()
        if out_type == "UTM":
            return TrxCoordType.from_utm_zone(self.cw.spinBox_output_utm_zone.value())
        return TrxCoordType(out_type)

    @property
    def t_coords(self) -> TrxCoordType:
        out_type = self.cw.comboBox_output_coordinates.currentText()
        if out_type == "UTM":
            return TrxCoordType.from_utm_zone(self.cw.spinBox_output_utm_zone.value())
        return TrxCoordType(out_type)

    @property
    def s_vd(self) -> TrxVd:
        return TrxVd(self.cw.comboBox_input_vertical_reference.currentText())

    @property
    def t_vd(self) -> TrxVd:
        return TrxVd(self.cw.comboBox_output_vertical_reference.currentText())

    @property
    def transform_config(self) -> TransformConfig:
        origin = ReferenceConfig(
            ref_frame=self.s_ref_frame,
            epoch=self.s_epoch,
            vd=self.s_vd,
            coord_type=self.s_coords,
        )
        destination = ReferenceConfig(
            ref_frame=self.t_ref_frame,
            epoch=self.t_epoch,
            vd=self.t_vd,
            coord_type=self.t_coords,
        )
        return TransformConfig(
            origin=origin, 
            destination=destination, 
            max_workers=self.cw.spinBox_worker_cores.value()
        )

    @transform_config.setter
    def transform_config(self, config: TransformConfig):
        self.cw.comboBox_input_reference.setCurrentText(config.origin.ref_frame.value)
        self.cw.dateEdit_input_epoch.setDate(config.origin.epoch)
        if config.origin.coord_type.is_utm():
            self.cw.spinBox_input_utm_zone.setValue(config.origin.coord_type.utm_zone)
            self.cw.comboBox_input_coordinates.setCurrentText("UTM")
        else:
            self.cw.comboBox_input_coordinates.setCurrentText(config.origin.coord_type.value)
        self.cw.comboBox_input_vertical_reference.setCurrentText(config.origin.vd.value)

        self.cw.comboBox_output_reference.setCurrentText(config.destination.ref_frame.value)
        self.cw.dateEdit_output_epoch.setDate(config.destination.epoch)
        if config.destination.coord_type.is_utm():
            self.cw.spinBox_output_utm_zone.setValue(config.destination.coord_type.utm_zone)
            self.cw.comboBox_output_coordinates.setCurrentText("UTM")
        else:
            self.cw.comboBox_output_coordinates.setCurrentText(config.destination.coord_type.value)
        self.cw.comboBox_output_vertical_reference.setCurrentText(config.destination.vd.value)
        
        self.cw.spinBox_worker_cores.setValue(config.max_workers)

        if config.origin.epoch != config.destination.epoch:
            self.cw.checkBox_epoch_trans.setChecked(True)

    @property
    def input_pattern(self) -> str:
        return rf"{self.cw.lineEdit_input_file.text()}"

    @property
    def output_pattern(self) -> str:
        return rf"{self.cw.lineEdit_output_file.text()}"

    def append_text(self, text):
        self.cw.textBrowser_log_output.moveCursor(QTextCursor.MoveOperation.End)
        self.cw.textBrowser_log_output.insertPlainText(text)

    def on_process_success(self):
        logger.info("Processing complete")
        self.done_msg_box.exec()

    def on_process_error(self, exception: BaseException):
        logger.error(str(exception))
        self.err_msg_box.showMessage(str(exception))
        self.err_msg_box.exec()

    def convert(self):
        logger.debug("Starting worker thread.")

        self.thread = TransformWorker(self.transform_config, self.input_pattern, self.output_pattern)

        self.thread.progress.connect(self.cw.progressBar.setValue)
        self.thread.success.connect(self.on_process_success)
        self.thread.error.connect(self.on_process_error)
        self.thread.started.connect(lambda: self.cw.pushButton_convert.setEnabled(False))
        self.thread.finished.connect(lambda: self.cw.pushButton_convert.setEnabled(True))
        self.thread.finished.connect(lambda: self.cw.progressBar.setValue(0))

        self.thread.start()


class LogWriteStream:
    def __init__(self, queue_):
        super().__init__()
        self.queue = queue_

    def write(self, text):
        self.queue.put(text)


class LogDisplayThread(QThread):
    on_msg = Signal(str)

    def __init__(self, queue_: Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue_

    def run(self):
        while not self.isInterruptionRequested():
            try:
                text = self.queue.get(block=False)
                self.on_msg.emit(text)
            except queue.Empty:
                continue


if __name__ == "__main__":
    freeze_support()

    # Configure logging
    log_msg_queue = Queue()
    log_write_stream = LogWriteStream(log_msg_queue)
    log_handler = logging.StreamHandler(log_write_stream)

    log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
    logging.basicConfig(level=log_level, handlers=[log_handler])

    app = QApplication(sys.argv)
    window = MainWindow()

    if os.getenv("DEBUG"):
        window.lineEdit_input_file.setText("/home/taylor/PycharmProjects/Las-TRX/testfiles/20_3028_01/*.laz")
        window.comboBox_input_reference.setCurrentText("ITRF2014")
        window.dateEdit_input_epoch.setDate(date(2020, 8, 12))

        window.lineEdit_output_file.setText(
            "/home/taylor/PycharmProjects/Las-TRX/testfiles/20_3028_01_converted/{}.laz"
        )
        window.checkBox_epoch_trans.setChecked(True)
        window.dateEdit_output_epoch.setEnabled(True)
        window.dateEdit_output_epoch.setDate(date(2002, 1, 1))
        window.comboBox_output_vertical_reference.setCurrentText("CGVD2013/CGG2013a")

    window.show()

    # When a new message is written to the log_queue via the log_write_stream,
    #   log_thread emits a signal that causes the main
    #   window to display that msg in the textBrowser
    log_thread = LogDisplayThread(log_msg_queue)
    log_thread.on_msg.connect(window.append_text)
    app.aboutToQuit.connect(log_thread.requestInterruption)
    log_thread.start()

    sys.exit(app.exec())

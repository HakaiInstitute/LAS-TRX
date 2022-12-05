import logging
import os.path
import queue
from datetime import date
from multiprocessing import freeze_support
from pathlib import Path
from queue import Queue

import sys
from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSignal as Signal
from PyQt6.QtGui import QIcon, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QErrorMessage,
    QFileDialog,
    QMessageBox,
    QWidget,
)

from csrspy.enums import CoordType, Reference, VerticalDatum
from las_trx import __version__ as las_trx_version
from las_trx.config import TransformConfig
from las_trx.utils import (
    REFERENCE_LOOKUP,
    VD_LOOKUP,
    sync_missing_grid_files,
    utm_zone_to_coord_type,
    resource_path,
)
from las_trx.worker import TransformWorker

logger = logging.getLogger(__name__)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("resources/mainwindow.ui"), self)

        # Setup window
        self.setWindowIcon(QIcon(resource_path("resources/las-trx.ico")))
        self.setWindowTitle(f"LAS TRX v{las_trx_version}")

        self.done_msg_box = QMessageBox(self)
        self.done_msg_box.setText("File(s) converted successfully")
        self.done_msg_box.setWindowTitle("Success")
        self.err_msg_box = QErrorMessage(self)
        self.err_msg_box.setWindowTitle("Error")
        self.help_msg_box = QMessageBox(self)
        self.help_msg_box.setText(
            "Use '*' in the input file to select multiple files.\n"
            "e.g. `C:\\\\path\\to\\files\\*.laz`\n\n"
            "Use '{}' in the output file to generate a name from the input name.\n"
            "e.g. `C:\\\\path\\to\\files\\{}_nad83.laz`"
        )
        self.help_msg_box.setWindowTitle("Help")

        self.toolButton_input_file.clicked.connect(self.handle_select_input_file)
        self.toolButton_output_file.clicked.connect(self.handle_select_output_file)
        self.checkBox_epoch_trans.clicked.connect(self.enable_epoch_trans)
        self.pushButton_convert.clicked.connect(self.convert)
        self.comboBox_input_reference.currentTextChanged.connect(
            self.update_input_vd_options
        )
        self.comboBox_output_reference.currentTextChanged.connect(
            self.update_output_vd_options
        )
        self.dateEdit_input_epoch.dateChanged.connect(self.maybe_update_output_epoch)
        self.comboBox_output_coordinates.currentTextChanged.connect(
            self.activate_output_utm_zone_picker
        )
        self.comboBox_input_coordinates.currentTextChanged.connect(
            self.activate_input_utm_zone_picker
        )
        self.toolButton_help.clicked.connect(self.help_msg_box.exec)

        self.dialog_directory = os.path.expanduser("~")

        self.thread = None

        sync_missing_grid_files()

    def maybe_update_output_epoch(self, new_date: date):
        if not self.checkBox_epoch_trans.isChecked():
            self.dateEdit_output_epoch.setDate(new_date)

    def handle_select_input_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input LAS file",
            directory=self.dialog_directory,
            filter="LAS Files (*.las *.laz)",
        )
        if path:
            self.lineEdit_input_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def handle_select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select output LAS file",
            directory=self.dialog_directory,
            filter="LAS Files (*.las *.laz)",
        )
        if path:
            self.lineEdit_output_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def enable_epoch_trans(self, checked):
        self.dateEdit_output_epoch.setEnabled(checked)

        if not checked:
            self.dateEdit_output_epoch.setDate(self.dateEdit_input_epoch.date())

    def activate_input_utm_zone_picker(self, text):
        self.spinBox_input_utm_zone.setEnabled(text == "UTM")

    def activate_output_utm_zone_picker(self, text):
        self.spinBox_output_utm_zone.setEnabled(text == "UTM")

    @staticmethod
    def update_vd_options(text, combo_box):
        combo_box.clear()
        if text == "NAD83(CSRS)":
            combo_box.addItems(
                ["GRS80", "CGVD2013/CGG2013a", "CGVD2013/CGG2013", "CGVD28/HT2_2010v70"]
            )
        elif text == "WGS84":
            combo_box.addItems(["WGS84"])
        else:
            combo_box.addItems(["GRS80"])

    def update_input_vd_options(self, text):
        self.update_vd_options(text, self.comboBox_input_vertical_reference)

    def update_output_vd_options(self, text):
        self.update_vd_options(text, self.comboBox_output_vertical_reference)

    @property
    def s_ref_frame(self) -> Reference:
        return REFERENCE_LOOKUP[self.comboBox_input_reference.currentText()]

    @property
    def t_ref_frame(self) -> Reference:
        return REFERENCE_LOOKUP[self.comboBox_output_reference.currentText()]

    @property
    def s_epoch(self) -> date:
        return self.dateEdit_input_epoch.date().toPyDate()

    @property
    def t_epoch(self) -> date:
        if self.checkBox_epoch_trans.isChecked():
            return self.dateEdit_output_epoch.date().toPyDate()
        else:
            return self.s_epoch

    @property
    def s_coords(self) -> CoordType:
        out_type = self.comboBox_input_coordinates.currentText()
        if out_type == "UTM":
            return utm_zone_to_coord_type(self.spinBox_output_utm_zone.value())
        elif out_type == "Cartesian":
            return CoordType.CART
        else:
            return CoordType.GEOG

    @property
    def t_coords(self) -> CoordType:
        out_type = self.comboBox_output_coordinates.currentText()
        if out_type == "UTM":
            return utm_zone_to_coord_type(self.spinBox_output_utm_zone.value())
        elif out_type == "Cartesian":
            return CoordType.CART
        else:
            return CoordType.GEOG

    @property
    def s_vd(self) -> VerticalDatum:
        return VD_LOOKUP[self.comboBox_input_vertical_reference.currentText()]

    @property
    def t_vd(self) -> VerticalDatum:
        return VD_LOOKUP[self.comboBox_output_vertical_reference.currentText()]

    @property
    def transform_config(self) -> TransformConfig:
        return TransformConfig(
            s_ref_frame=self.s_ref_frame,
            t_ref_frame=self.t_ref_frame,
            s_epoch=self.s_epoch,
            t_epoch=self.t_epoch,
            s_vd=self.s_vd,
            t_vd=self.t_vd,
            s_coords=self.s_coords,
            t_coords=self.t_coords,
        )

    @property
    def input_files(self) -> list[Path]:
        p = Path(self.lineEdit_input_file.text())
        return [f for f in p.parent.glob(p.name) if f.is_file()]

    @property
    def output_files(self) -> list[Path]:
        out_path = self.lineEdit_output_file.text()
        return [Path(out_path.format(f.stem)) for f in self.input_files]

    def append_text(self, text):
        self.textBrowser_log_output.moveCursor(QTextCursor.MoveOperation.End)
        self.textBrowser_log_output.insertPlainText(text)

    def on_process_success(self):
        logger.info("Processing complete")
        self.done_msg_box.exec()

    def on_process_error(self, exception: BaseException):
        logger.error(str(exception))
        self.err_msg_box.showMessage(str(exception))
        self.err_msg_box.exec()

    def convert(self):
        logger.debug("Starting worker thread.")

        self.thread = TransformWorker(
            self.transform_config, self.input_files, self.output_files
        )

        self.thread.progress.connect(self.progressBar.setValue)
        self.thread.success.connect(self.on_process_success)
        self.thread.error.connect(self.on_process_error)
        self.thread.started.connect(lambda: self.pushButton_convert.setEnabled(False))
        self.thread.finished.connect(lambda: self.pushButton_convert.setEnabled(True))
        self.thread.finished.connect(lambda: self.progressBar.setValue(0))

        self.thread.start()


class LogWriteStream(object):
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

    logging.basicConfig(level=logging.INFO, handlers=[log_handler])

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # When a new message is written to the log_queue via the log_write_stream, log_thread emits a signal that causes the main
    # When a new message is written to the log_queue via the log_write_stream,
    #   log_thread emits a signal that causes the main
    #   window to display that msg in the textBrowser
    log_thread = LogDisplayThread(log_msg_queue)
    log_thread.on_msg.connect(window.append_text)
    app.aboutToQuit.connect(log_thread.requestInterruption)
    log_thread.start()

    sys.exit(app.exec())

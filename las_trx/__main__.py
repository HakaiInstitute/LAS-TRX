import logging
import os.path
import queue
import sys
from datetime import date
from multiprocessing import freeze_support
from queue import Queue

from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSignal as Signal
from PyQt6.QtGui import QIcon, QTextCursor, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QErrorMessage,
    QFileDialog,
    QMessageBox,
    QWidget,
    QMenuBar,
    QMenu,
)

from csrspy.utils import sync_missing_grid_files
from las_trx import __version__
from las_trx.config import TransformConfig, ReferenceConfig, TrxReference, TrxVd, TrxCoordType
from las_trx.utils import (
    resource_path,
    get_upgrade_version
)
from las_trx.worker import TransformWorker

logger = logging.getLogger(__name__)


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

        # Setup window
        self.setWindowIcon(QIcon(resource_path("resources/las-trx.ico")))
        self.setWindowTitle(f"LAS TRX v{__version__}")

        # Create menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create File menu
        file_menu = QMenu("File", self)
        self.menu_bar.addMenu(file_menu)
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)

        # Create config menu
        config_menu = QMenu("Config", self)
        self.menu_bar.addMenu(config_menu)
        save_config_action = config_menu.addAction("Save")
        save_config_action.setShortcut(QKeySequence.StandardKey.Save)
        save_config_action.triggered.connect(self.save_config)
        load_config_action = config_menu.addAction("Load")
        load_config_action.setShortcut(QKeySequence.StandardKey.Open)
        load_config_action.triggered.connect(self.load_config)

        # Create Log menu
        log_menu = QMenu("Logs", self)
        self.menu_bar.addMenu(log_menu)
        save_log_action = log_menu.addAction("Save")
        save_log_action.triggered.connect(self.save_log)
        clear_log_action = log_menu.addAction("Clear")
        clear_log_action.triggered.connect(self.clear_log)

        upgrade_version = get_upgrade_version(__version__)
        if upgrade_version is None:
            self.cw.label_upgrade_link.hide()
        else:
            self.cw.label_upgrade_link.setText(
                f"<a href=\"{upgrade_version['html_url']}\">"
                "<span style=\"text-decoration: underline; color:rgb(153, 193, 241)\">"
                f"New version available (v{upgrade_version['tag_name']})"
                f"</span></a>"
            )

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

        self.cw.toolButton_input_file.clicked.connect(self.handle_select_input_file)
        self.cw.toolButton_output_file.clicked.connect(self.handle_select_output_file)
        self.cw.checkBox_epoch_trans.clicked.connect(self.enable_epoch_trans)
        self.cw.pushButton_convert.clicked.connect(self.convert)
        self.cw.comboBox_input_reference.currentTextChanged.connect(
            self.update_input_vd_options
        )
        self.cw.comboBox_output_reference.currentTextChanged.connect(
            self.update_output_vd_options
        )
        self.cw.dateEdit_input_epoch.dateChanged.connect(self.maybe_update_output_epoch)
        self.cw.comboBox_output_coordinates.currentTextChanged.connect(
            self.activate_output_utm_zone_picker
        )
        self.cw.comboBox_input_coordinates.currentTextChanged.connect(
            self.activate_input_utm_zone_picker
        )
        self.cw.toolButton_help.clicked.connect(self.help_msg_box.exec)

        self.dialog_directory = os.path.expanduser("~")

        self.thread = None

        sync_missing_grid_files()

    def save_config(self):
        logger.info("Saving config")

    def load_config(self):
        logger.info("Loading config")

    def save_log(self):
        pass

    def clear_log(self):
        pass

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
        return TransformConfig(origin=origin, destination=destination)

    @property
    def input_pattern(self) -> str:
        return self.cw.lineEdit_input_file.text()

    @property
    def output_pattern(self) -> str:
        return self.cw.lineEdit_output_file.text()

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

        self.thread = TransformWorker(
            self.transform_config, self.input_pattern, self.output_pattern
        )

        self.thread.progress.connect(self.cw.progressBar.setValue)
        self.thread.success.connect(self.on_process_success)
        self.thread.error.connect(self.on_process_error)
        self.thread.started.connect(
            lambda: self.cw.pushButton_convert.setEnabled(False)
        )
        self.thread.finished.connect(
            lambda: self.cw.pushButton_convert.setEnabled(True)
        )
        self.thread.finished.connect(lambda: self.cw.progressBar.setValue(0))

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

    log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
    logging.basicConfig(level=log_level, handlers=[log_handler])

    app = QApplication(sys.argv)
    window = MainWindow()

    if os.getenv("DEBUG"):
        window.lineEdit_input_file.setText(
            "/home/taylor/PycharmProjects/Las-TRX/testfiles/20_3028_01/*.laz"
        )
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

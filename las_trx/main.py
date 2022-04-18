import os.path
import sys
from datetime import date
from multiprocessing import freeze_support
from pathlib import Path

from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QErrorMessage,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)
from csrspy.enums import CoordType, Reference, VerticalDatum

from las_trx.config import TransformConfig
from las_trx.ui_mainwindow import Ui_MainWindow
from las_trx.utils import (
    REFERENCE_LOOKUP,
    VD_LOOKUP,
    sync_missing_grid_files,
    utm_zone_to_coord_type,
)
from las_trx.worker import TransformWorker


def resource_path(relative_path: str):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        icon = QIcon()
        icon.addFile(
            resource_path("resources/las-trx.ico"), QSize(), QIcon.Normal, QIcon.Off
        )
        self.setWindowIcon(icon)

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

        self.ui.toolButton_input_file.clicked.connect(self.handle_select_input_file)
        self.ui.toolButton_output_file.clicked.connect(self.handle_select_output_file)
        self.ui.checkBox_epoch_trans.clicked.connect(self.enable_epoch_trans)
        self.ui.pushButton_convert.clicked.connect(self.convert)
        self.ui.comboBox_input_reference.currentTextChanged.connect(
            self.update_input_vd_options
        )
        self.ui.comboBox_output_reference.currentTextChanged.connect(
            self.update_output_vd_options
        )
        self.ui.dateEdit_input_epoch.dateChanged.connect(self.maybe_update_output_epoch)
        self.ui.comboBox_output_coordinates.currentTextChanged.connect(
            self.activate_output_utm_zone_picker
        )
        self.ui.comboBox_input_coordinates.currentTextChanged.connect(
            self.activate_input_utm_zone_picker
        )
        self.ui.toolButton_help.clicked.connect(self.help_msg_box.exec_)

        self.dialog_directory = os.path.expanduser("~")

        self.thread = None

        sync_missing_grid_files()

    def maybe_update_output_epoch(self, new_date: date):
        if not self.ui.checkBox_epoch_trans.isChecked():
            self.ui.dateEdit_output_epoch.setDate(new_date)

    def handle_select_input_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input LAS file",
            dir=self.dialog_directory,
            filter="LAS Files (*.las *.laz)",
        )
        if path:
            self.ui.lineEdit_input_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def handle_select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select output LAS file",
            dir=self.dialog_directory,
            filter="LAS Files (*.las *.laz)",
        )
        if path:
            self.ui.lineEdit_output_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def enable_epoch_trans(self, checked):
        self.ui.dateEdit_output_epoch.setEnabled(checked)

        if not checked:
            self.ui.dateEdit_output_epoch.setDate(self.ui.dateEdit_input_epoch.date())

    def activate_input_utm_zone_picker(self, text):
        self.ui.spinBox_input_utm_zone.setEnabled(text == "UTM")

    def activate_output_utm_zone_picker(self, text):
        self.ui.spinBox_output_utm_zone.setEnabled(text == "UTM")

    def update_input_vd_options(self, text):
        self.ui.comboBox_input_vertical_reference.clear()
        if text == "NAD83(CSRS)":
            self.ui.comboBox_input_vertical_reference.addItems(
                ["GRS80", "CGVD2013/CGG2013a", "CGVD2013/CGG2013", "CGVD28/HT2_2010v70"]
            )
        else:
            self.ui.comboBox_input_vertical_reference.addItems(["GRS80"])

    def update_output_vd_options(self, text):
        self.ui.comboBox_output_vertical_reference.clear()
        if text == "NAD83(CSRS)":
            self.ui.comboBox_output_vertical_reference.addItems(
                ["GRS80", "CGVD2013/CGG2013a", "CGVD2013/CGG2013", "CGVD28/HT2_2010v70"]
            )
        else:
            self.ui.comboBox_output_vertical_reference.addItems(["GRS80"])

    @property
    def s_ref_frame(self) -> Reference:
        return REFERENCE_LOOKUP[self.ui.comboBox_input_reference.currentText()]

    @property
    def t_ref_frame(self) -> Reference:
        return REFERENCE_LOOKUP[self.ui.comboBox_output_reference.currentText()]

    @property
    def s_epoch(self) -> date:
        return self.ui.dateEdit_input_epoch.date().toPython()

    @property
    def t_epoch(self) -> date:
        if self.ui.checkBox_epoch_trans.isChecked():
            return self.ui.dateEdit_output_epoch.date().toPython()
        else:
            return self.s_epoch

    @property
    def s_coords(self) -> CoordType:
        out_type = self.ui.comboBox_input_coordinates.currentText()
        if out_type == "UTM":
            return utm_zone_to_coord_type(self.ui.spinBox_output_utm_zone.value())
        elif out_type == "Cartesian":
            return CoordType.CART
        else:
            return CoordType.GEOG

    @property
    def t_coords(self) -> CoordType:
        out_type = self.ui.comboBox_output_coordinates.currentText()
        if out_type == "UTM":
            return utm_zone_to_coord_type(self.ui.spinBox_output_utm_zone.value())
        elif out_type == "Cartesian":
            return CoordType.CART
        else:
            return CoordType.GEOG

    @property
    def s_vd(self) -> VerticalDatum:
        return VD_LOOKUP[self.ui.comboBox_input_vertical_reference.currentText()]

    @property
    def t_vd(self) -> VerticalDatum:
        return VD_LOOKUP[self.ui.comboBox_output_vertical_reference.currentText()]

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
        p = Path(self.ui.lineEdit_input_file.text())
        return [f for f in p.parent.glob(p.name) if f.is_file()]

    @property
    def output_files(self) -> list[Path]:
        out_path = self.ui.lineEdit_output_file.text()
        return [Path(out_path.format(f.stem)) for f in self.input_files]

    def on_process_success(self):
        self.done_msg_box.exec()

    def on_process_error(self, exception: BaseException):
        self.err_msg_box.showMessage(str(exception))
        self.err_msg_box.exec()

    def convert(self):
        self.thread = TransformWorker(
            self.transform_config, self.input_files, self.output_files
        )

        self.thread.progress.connect(self.ui.progressBar.setValue)
        self.thread.success.connect(self.on_process_success)
        self.thread.error.connect(self.on_process_error)
        self.thread.started.connect(
            lambda: self.ui.pushButton_convert.setEnabled(False)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_convert.setEnabled(True)
        )
        self.thread.finished.connect(lambda: self.ui.progressBar.setValue(0))

        self.thread.start()


if __name__ == "__main__":
    freeze_support()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

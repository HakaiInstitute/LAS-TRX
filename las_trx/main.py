import math
import os.path
import subprocess
import sys
from datetime import date
from typing import Optional

import laspy
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QErrorMessage, QFileDialog, QMainWindow, QMessageBox
from csrspy import CSRSTransformer, enums

from las_trx.config import TransformConfig
from las_trx.ui_mainwindow import Ui_MainWindow
from las_trx.utils import GEOID_LOOKUP, REFERENCE_LOOKUP

CHUNK_SIZE = 1_000


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.done_msg_box = QMessageBox(self)
        self.done_msg_box.setText("File was converted successfully")
        self.done_msg_box.setWindowTitle("LAS TRX Message")
        self.err_msg_box = QErrorMessage(self)
        self.err_msg_box.setWindowTitle("LAS TRX Error")

        self.ui.toolButton_input_file.clicked.connect(self.handle_select_input_file)
        self.ui.toolButton_output_file.clicked.connect(self.handle_select_output_file)
        self.ui.checkBox_epoch_trans.clicked.connect(self.enable_epoch_trans)
        self.ui.checkBox_vd_trans.clicked.connect(self.enable_vd_trans)
        self.ui.pushButton_convert.clicked.connect(self.convert)
        self.ui.comboBox_output_coordinates.currentTextChanged.connect(self.activate_output_utm_zone_picker)
        self.ui.comboBox_input_coordinates.currentTextChanged.connect(self.activate_input_utm_zone_picker)
        self.ui.comboBox_vertical_datum.currentTextChanged.connect(self.update_geoid_options)

        self.dialog_directory = os.path.expanduser("~")

        self.thread = TransformWorker()
        self.thread.progress.connect(self.ui.progressBar.setValue)
        self.thread.success.connect(self.on_process_success)
        self.thread.error.connect(self.on_process_error)
        self.thread.started.connect(lambda: self.ui.pushButton_convert.setEnabled(False))
        self.thread.finished.connect(lambda: self.ui.pushButton_convert.setEnabled(True))
        self.thread.finished.connect(lambda: self.ui.progressBar.setValue(0))

        self.sync_grid_files()

    @staticmethod
    def sync_grid_files():
        p = subprocess.Popen(['pyproj', 'sync', '--area-of-use=Canada'])
        p.wait()

    def handle_select_input_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select input LAS file", dir=self.dialog_directory,
                                              filter="LAS Files (*.las *.laz)")
        if path:
            self.ui.lineEdit_input_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def handle_select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select output LAS file", dir=self.dialog_directory,
                                              filter="LAS Files (*.las *.laz)")
        if path:
            self.ui.lineEdit_output_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def enable_epoch_trans(self, checked):
        self.ui.dateEdit_output_epoch.setEnabled(checked)

    def enable_vd_trans(self, checked):
        self.ui.comboBox_vertical_datum.setEnabled(checked)
        self.ui.comboBox_output_geoid.setEnabled(checked)

    def activate_input_utm_zone_picker(self, text):
        self.ui.spinBox_input_utm_zone.setEnabled(text == "UTM")

    def activate_output_utm_zone_picker(self, text):
        self.ui.spinBox_output_utm_zone.setEnabled(text == "UTM")

    def update_geoid_options(self, text):
        self.ui.comboBox_output_geoid.clear()
        if text == 'CGVD28':
            self.ui.comboBox_output_geoid.addItems(["HT2_2010v70"])
        else:
            self.ui.comboBox_output_geoid.addItems(["CGG2013a", "CGG2013"])

    @property
    def s_ref_frame(self) -> enums.Ref:
        return REFERENCE_LOOKUP[self.ui.comboBox_input_reference.currentText()]

    @property
    def s_epoch(self) -> date:
        return self.ui.dateEdit_input_epoch.date().toPython()

    @property
    def t_epoch(self) -> Optional[date]:
        if self.ui.checkBox_epoch_trans.isChecked():
            return self.ui.dateEdit_output_epoch.date().toPython()

    @property
    def out_coordinates(self) -> str:
        out_type = self.ui.comboBox_output_coordinates.currentText()
        if out_type == "UTM":
            return f"utm{self.ui.spinBox_output_utm_zone.value()}"
        elif out_type == "Cartesian":
            return "cart"
        else:
            return "geog"

    @property
    def t_vd(self) -> Optional[enums.Geoid]:
        if self.ui.checkBox_vd_trans.isChecked():
            return GEOID_LOOKUP[self.ui.comboBox_output_geoid.currentText()]

    @property
    def s_crs(self) -> str:
        coords = self.ui.comboBox_input_coordinates.currentText()
        if coords == "Cartesian":
            return "+proj=cart +datum=WGS84 +no_defs"
        elif coords == "Geographic":
            return "+proj=longlat +datum=WGS84 +no_defs"
        else:
            zone = self.ui.spinBox_input_utm_zone.value()
            return f"+proj=utm +zone={zone} +datum=WGS84 +units=m +no_defs"

    @property
    def transform_config(self) -> TransformConfig:
        return TransformConfig(
            s_ref_frame=self.s_ref_frame,
            s_crs=self.s_crs,
            s_epoch=self.s_epoch,
            t_epoch=self.t_epoch,
            t_vd=self.t_vd,
            out=self.out_coordinates
        )

    @property
    def input_file(self) -> str:
        return self.ui.lineEdit_input_file.text()

    @property
    def output_file(self) -> str:
        return self.ui.lineEdit_output_file.text()

    @property
    def do_compress_output(self) -> bool:
        return self.input_file[-4:] == ".laz"

    @property
    def laz_backend(self) -> Optional[laspy.LazBackend]:
        if self.do_compress_output:
            return laspy.LazBackend.Laszip

    def on_process_success(self):
        self.done_msg_box.exec()

    def on_process_error(self, exception: BaseException):
        self.err_msg_box.showMessage(str(exception))
        self.err_msg_box.exec()

    def convert(self):
        self.thread.setup(self.transform_config, self.input_file, self.output_file, self.laz_backend)
        self.thread.start()


class TransformWorker(QThread):
    started = Signal()
    finished = Signal()
    progress = Signal(int)
    success = Signal()
    error = Signal(BaseException)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.config = None
        self.input_file = None
        self.output_file = None
        self.compression = None

    def setup(self, config: TransformConfig, input_file: str, output_file: str, compression=None):
        self.config = config
        self.input_file = input_file
        self.output_file = output_file
        self.compression = compression

    def _do_transform(self):
        transformer = CSRSTransformer(**self.config.dict(exclude_none=True))

        with laspy.open(self.input_file) as in_las, \
                laspy.open(self.output_file, mode='w', header=in_las.header, laz_backend=self.compression) as out_las:

            # TODO: Automate setting these values in a way that matches PDALs writers.las
            out_las.header.offsets = None  # Adjusted later using first batch
            out_las.header.scales = np.array([1e-7, 1e-7, 1e-7])

            total_iters = math.ceil(in_las.header.point_count / CHUNK_SIZE)
            for i, points in enumerate(in_las.chunk_iterator(CHUNK_SIZE)):
                # Convert the coordinates
                data = np.stack((points.x.scaled_array(), points.y.scaled_array(), points.z.scaled_array())).T
                data = np.array(list(transformer.forward(data)))

                # Update header offsets
                if out_las.header.offsets is None:
                    out_las.header.offsets = np.min(data, axis=0)

                # Create new point records
                points.change_scaling(offsets=out_las.header.offsets)
                points.x = data[:, 0]
                points.y = data[:, 1]
                points.z = data[:, 2]
                out_las.write_points(points)

                self.progress.emit(int(100 * (i + 1) / float(total_iters)))

    def run(self):
        self.started.emit()

        try:
            self._do_transform()
            self.success.emit()
        except Exception as e:
            self.error.emit(e)

        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

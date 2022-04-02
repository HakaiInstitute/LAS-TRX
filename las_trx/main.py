import math
import os.path
import sys
from datetime import date
from typing import Callable, Optional

import laspy
import numpy as np
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

        self.sync_grid_files()

    @staticmethod
    def sync_grid_files():
        os.system('pyproj sync --area-of-use=Canada')

    def handle_select_input_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select input LAS file", dir=self.dialog_directory,
                                              filter="LAS Files (*.las, *.laz)")
        if path:
            self.ui.lineEdit_input_file.setText(path)
            self.dialog_directory = os.path.dirname(path)

    def handle_select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select output LAS file", dir=self.dialog_directory,
                                              filter="LAS Files (*.las, *.laz)")
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
            return self.ui.dateEdit_input_epoch.date().toPython()

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
        if self.ui.checkBox_vd_trans:
            return GEOID_LOOKUP[self.ui.comboBox_output_geoid.currentText()]

    @property
    def s_crs(self) -> str:
        coords = self.ui.comboBox_input_coordinates.currentText()
        if coords == "Cartesian":
            return "+proj=cart +ellps=GRS80"
        elif coords == "Geographic":
            return "+proj=latlon +datum=WGS84"
        else:
            zone = self.ui.spinBox_input_utm_zone.value()
            return f"+proj=utm +zone={zone} +ellps=GRS80"

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

    def update_progress(self, value: float):
        self.ui.progressBar.setValue(int(value * 100))

    def set_convert_button_enabled(self, enabled):
        self.ui.pushButton_convert.setEnabled(enabled)

    def convert(self):
        self.set_convert_button_enabled(False)

        try:
            transform_file(self.transform_config, self.input_file, self.output_file, self.update_progress)
            self.done_msg_box.exec()
        except Exception as e:
            self.err_msg_box.showMessage(str(e))
            self.err_msg_box.exec()

        self.update_progress(0)
        self.set_convert_button_enabled(True)


def transform_file(config: TransformConfig, input_file: str, output_file: str, iter_callback: Callable[[float], None]):
    transformer = CSRSTransformer(**config.dict(exclude_none=True))

    with laspy.open(input_file) as in_las, \
            laspy.open(output_file, mode='w', header=in_las.header) as out_las:

        out_las.header.offsets = None  # Adjusted later using first batch
        if config.out == "geog":
            out_las.header.scales = np.array([1e-6, 1e-6, 0.001])
        else:
            out_las.header.scales = np.array([0.01, 0.01, 0.01])

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

            iter_callback(((i + 1) / float(total_iters)))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

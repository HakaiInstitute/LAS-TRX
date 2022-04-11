import math
import os.path
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import laspy
import numpy as np
from PySide2.QtCore import QSize, QThread, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QErrorMessage, QFileDialog, QMainWindow, QMessageBox
from csrspy import CSRSTransformer
from csrspy.enums import CoordType, Reference, VerticalDatum

from las_trx.config import TransformConfig
from las_trx.ui_mainwindow import Ui_MainWindow
from las_trx.utils import REFERENCE_LOOKUP, VD_LOOKUP, sync_missing_grid_files, \
    utm_zone_to_coord_type
from las_trx.vlr import GeoAsciiParamsVlr, GeoKeyDirectoryVlr

CHUNK_SIZE = 10_000


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        icon = QIcon()
        icon.addFile(resource_path(u"resources/las-trx.ico"), QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        self.done_msg_box = QMessageBox(self)
        self.done_msg_box.setText("File(s) were converted successfully")
        self.done_msg_box.setWindowTitle("LAS TRX Message")
        self.err_msg_box = QErrorMessage(self)
        self.err_msg_box.setWindowTitle("LAS TRX Error")

        self.ui.toolButton_input_file.clicked.connect(self.handle_select_input_file)
        self.ui.toolButton_output_file.clicked.connect(self.handle_select_output_file)
        self.ui.checkBox_epoch_trans.clicked.connect(self.enable_epoch_trans)
        self.ui.pushButton_convert.clicked.connect(self.convert)
        self.ui.comboBox_input_reference.currentTextChanged.connect(self.update_input_vd_options)
        self.ui.comboBox_output_reference.currentTextChanged.connect(self.update_output_vd_options)
        self.ui.dateEdit_input_epoch.dateChanged.connect(self.maybe_update_output_epoch)
        self.ui.comboBox_output_coordinates.currentTextChanged.connect(self.activate_output_utm_zone_picker)
        self.ui.comboBox_input_coordinates.currentTextChanged.connect(self.activate_input_utm_zone_picker)
        self.ui.comboBox_output_vertical_reference.currentTextChanged.connect(self.maybe_force_output_epoch_change)
        self.ui.comboBox_input_vertical_reference.currentTextChanged.connect(self.maybe_force_input_epoch_change)

        self.dialog_directory = os.path.expanduser("~")

        self.thread = TransformWorker()
        self.thread.progress.connect(self.ui.progressBar.setValue)
        self.thread.success.connect(self.on_process_success)
        self.thread.error.connect(self.on_process_error)
        self.thread.started.connect(lambda: self.ui.pushButton_convert.setEnabled(False))
        self.thread.finished.connect(lambda: self.ui.pushButton_convert.setEnabled(True))
        self.thread.finished.connect(lambda: self.ui.progressBar.setValue(0))

        sync_missing_grid_files()

    def maybe_force_input_epoch_change(self, new_in_vd: str):
        if new_in_vd == "CGVD28/HT2_2010v70":
            self.ui.dateEdit_input_epoch.setDate(date(2010, 1, 1))
            self.ui.dateEdit_input_epoch.setEnabled(False)
        else:
            self.ui.dateEdit_input_epoch.setEnabled(True)

    def maybe_force_output_epoch_change(self, new_out_vd: str):
        if new_out_vd == "CGVD28/HT2_2010v70":
            self.ui.checkBox_epoch_trans.setChecked(True)
            self.ui.checkBox_epoch_trans.setEnabled(False)
            self.ui.dateEdit_output_epoch.setDate(date(2010, 1, 1))
            self.ui.dateEdit_output_epoch.setEnabled(False)
        else:
            self.ui.checkBox_epoch_trans.setEnabled(True)
            if self.ui.checkBox_epoch_trans.isChecked():
                self.ui.dateEdit_output_epoch.setEnabled(True)

    def maybe_update_output_epoch(self, new_date: date):
        if not self.ui.checkBox_epoch_trans.isChecked():
            self.ui.dateEdit_output_epoch.setDate(new_date)

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

        if not checked:
            self.ui.dateEdit_output_epoch.setDate(self.ui.dateEdit_input_epoch.date())

    def activate_input_utm_zone_picker(self, text):
        self.ui.spinBox_input_utm_zone.setEnabled(text == "UTM")

    def activate_output_utm_zone_picker(self, text):
        self.ui.spinBox_output_utm_zone.setEnabled(text == "UTM")

    def update_input_vd_options(self, text):
        self.ui.comboBox_input_vertical_reference.clear()
        if text == 'NAD83(CSRS)':
            self.ui.comboBox_input_vertical_reference.addItems([
                "GRS80", "CGVD2013/CGG2013a", "CGVD2013/CGG2013", "CGVD28/HT2_2010v70"])
        else:
            self.ui.comboBox_input_vertical_reference.addItems(["GRS80"])

    def update_output_vd_options(self, text):
        self.ui.comboBox_output_vertical_reference.clear()
        if text == 'NAD83(CSRS)':
            self.ui.comboBox_output_vertical_reference.addItems([
                "GRS80", "CGVD2013/CGG2013a", "CGVD2013/CGG2013", "CGVD28/HT2_2010v70"])
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
            t_coords=self.t_coords
        )

    @property
    def input_files(self) -> list[str]:
        p = Path(self.ui.lineEdit_input_file.text())
        return [str(f) for f in (p.parent.glob(p.name))]

    @property
    def output_files(self) -> list[str]:
        p = self.ui.lineEdit_output_file.text()
        return [p.format(str(Path(f).stem)) for f in self.input_files]

    def on_process_success(self):
        self.done_msg_box.exec()

    def on_process_error(self, exception: BaseException):
        self.err_msg_box.showMessage(str(exception))
        self.err_msg_box.exec()

    def convert(self):
        self.thread.setup(self.transform_config, self.input_files, self.output_files)
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
        self.input_files = None
        self.output_files = None

    def setup(self, config: TransformConfig, input_files: list[str], output_files: list[str]):
        self.config = config
        self.input_files = input_files
        self.output_files = output_files

    @staticmethod
    def laz_backend(output_file: str) -> Optional[laspy.LazBackend]:
        if output_file[-4:] == ".laz":
            return laspy.LazBackend.Laszip

    def get_total_iters(self) -> int:
        total_iters = 0
        for input_file in self.input_files:
            with laspy.open(input_file) as in_las:
                total_iters += math.ceil(in_las.header.point_count / CHUNK_SIZE)

        return total_iters

    def check_file_names(self):
        for in_file, out_file in zip(self.input_files, self.output_files):
            if in_file == out_file:
                raise AssertionError("In path has as identical name to the output path. " \
                                     "Change it to prevent overwriting the file.")

        for i, out_file in enumerate(self.output_files[:-1]):
            if out_file in self.output_files[i + 1:]:
                raise AssertionError("Duplicate output file name detected. "
                                     "Use a format string for the output path to output a file based on the stem of the "
                                     r"corresponding input file. e.g. 'C:\\some\path\{}_nad83csrs.laz'")

    def _do_transform(self):
        self.check_file_names()

        transformer = CSRSTransformer(**self.config.dict(exclude_none=True))
        total_iters = self.get_total_iters()
        current_iter = 0

        for input_file, output_file in zip(self.input_files, self.output_files):
            with laspy.open(input_file) as in_las:
                new_header = in_las.header

                # Update GeoKeyDirectoryVLR
                # check and remove any existing crs vlrs
                for crs_vlr_name in (
                        "WktCoordinateSystemVlr",
                        "GeoKeyDirectoryVlr",
                        "GeoAsciiParamsVlr",
                        "GeoDoubleParamsVlr",
                ):
                    try:
                        new_header.vlrs.extract(crs_vlr_name)
                    except IndexError:
                        pass

                new_header.vlrs.append(GeoAsciiParamsVlr.from_crs(self.config.t_crs))
                new_header.vlrs.append(GeoKeyDirectoryVlr.from_crs(self.config.t_crs))
                new_header.scales = np.array([0.01, 0.01, 0.01])
                new_header.offsets = self.estimate_offsets(input_file, transformer)

                with laspy.open(output_file, mode='w', header=new_header,
                                laz_backend=self.laz_backend(output_file)) as out_las:
                    for points in in_las.chunk_iterator(CHUNK_SIZE):
                        # Convert the coordinates
                        data = self._stack_dims(points)
                        data = np.array(list(transformer(data)))

                        # Create new point records
                        points.change_scaling(offsets=new_header.offsets, scales=new_header.scales)
                        points.x = data[:, 0]
                        points.y = data[:, 1]
                        points.z = data[:, 2]
                        out_las.write_points(points)

                        self.progress.emit(int(100 * (current_iter + 1) / float(total_iters)))
                        current_iter += 1

    @staticmethod
    def _stack_dims(points):
        # Copy the points for performance. Makes the underlying arrays contiguous
        x = points.x.scaled_array().copy()
        y = points.y.scaled_array().copy()
        z = points.z.scaled_array().copy()
        return np.stack((x, y, z)).T

    def estimate_offsets(self, input_file: str, transformer: CSRSTransformer):
        with laspy.open(input_file) as in_las:
            points = next(in_las.chunk_iterator(CHUNK_SIZE))
            data = self._stack_dims(points)

            # Convert the coordinates
            data = np.array(list(transformer(data)))

            # Return estimated header offsets as min x,y,z of first batch
            return np.min(data, axis=0)

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

    sys.exit(app.exec_())

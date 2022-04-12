import math
import multiprocessing
from concurrent import futures
from pathlib import Path
from time import sleep

import laspy
import numpy as np
from PySide2.QtCore import QThread, Signal
from csrspy import CSRSTransformer
from laspy import LasHeader
from pyproj import CRS

from las_trx.config import TransformConfig
from las_trx.vlr import GeoAsciiParamsVlr, GeoKeyDirectoryVlr

CHUNK_SIZE = 10_000


class TransformWorker(QThread):
    started = Signal()
    finished = Signal()
    progress = Signal(int)
    success = Signal()
    error = Signal(BaseException)

    def __init__(
        self, config: TransformConfig, input_files: list[Path], output_files: list[Path]
    ):
        super().__init__(parent=None)
        self.config = config
        self.input_files = input_files
        self.output_files = output_files

        self.total_iters = 0
        for input_file in self.input_files:
            with laspy.open(input_file) as in_las:
                self.total_iters += math.ceil(in_las.header.point_count / CHUNK_SIZE)

        self.pool = futures.ProcessPoolExecutor()
        self.manager = multiprocessing.Manager()
        self.lock = self.manager.RLock()
        self.current_iter = self.manager.Value("i", 0)

    def check_file_names(self):
        for in_file in self.input_files:
            if in_file in self.output_files:
                raise AssertionError(
                    "One of in files matches name of output files. "
                    "Aborting because this would overwrite that input file."
                )

        if len(self.output_files) != len(list(set(self.output_files))):
            raise AssertionError(
                "Duplicate output file name detected. "
                "Use a format string for the output path to output a file based on the stem of the "
                r"corresponding input file. e.g. 'C:\\some\path\{}_nad83csrs.laz'"
            )

    def _do_transform(self):
        self.check_file_names()

        config = self.config.dict(exclude_none=True)
        futs = []
        for input_file, output_file in zip(self.input_files, self.output_files):
            fut = self.pool.submit(
                transform, config, input_file, output_file, self.lock, self.current_iter
            )
            fut.add_done_callback(self.on_process_complete)
            futs.append(fut)

        while any([f.running() for f in futs]):
            self.progress.emit(self.progress_val)
            sleep(0.1)
        self.progress.emit(self.progress_val)

    @staticmethod
    def on_process_complete(fut: futures.Future):
        err = fut.exception()
        if err is not None:
            raise err

    @property
    def progress_val(self):
        return int(100 * self.current_iter.value / float(self.total_iters))

    def run(self):
        self.started.emit()

        try:
            self._do_transform()
            self.success.emit()
        except Exception as e:
            self.error.emit(e)

        self.finished.emit()


def transform(
    config: dict,
    input_file: Path,
    output_file: Path,
    lock: multiprocessing.RLock,
    cur: multiprocessing.Value,
):
    transformer = CSRSTransformer(**config)
    config = TransformConfig(**config)

    with laspy.open(input_file) as in_las:
        new_header = in_las.header
        new_header = clear_header_geokeys(new_header)
        new_header = write_header_geokeys_from_crs(new_header, config.t_crs)
        new_header = write_header_scales(new_header)
        new_header = write_header_offsets(new_header, input_file, transformer)

        laz_backend = laspy.LazBackend.Laszip if output_file.suffix == ".laz" else None
        with laspy.open(
            output_file, mode="w", header=new_header, laz_backend=laz_backend
        ) as out_las:
            for points in in_las.chunk_iterator(CHUNK_SIZE):
                # Convert the coordinates
                data = stack_dims(points)
                data = np.array(list(transformer(data)))

                # Create new point records
                points.change_scaling(
                    offsets=new_header.offsets, scales=new_header.scales
                )
                points.x = data[:, 0]
                points.y = data[:, 1]
                points.z = data[:, 2]
                out_las.write_points(points)

                with lock:
                    cur.value += 1


def write_header_offsets(
    header: "LasHeader", input_file: Path, transformer: "CSRSTransformer"
) -> "LasHeader":
    with laspy.open(input_file) as in_las:
        points = next(in_las.chunk_iterator(CHUNK_SIZE))
        data = stack_dims(points)

        # Convert the coordinates
        data = np.array(list(transformer(data)))

        # Return estimated header offsets as min x,y,z of first batch
        header.offsets = np.min(data, axis=0)
    return header


def clear_header_geokeys(header: "LasHeader") -> "LasHeader":
    # Update GeoKeyDirectoryVLR
    # check and remove any existing crs vlrs
    for crs_vlr_name in (
        "WktCoordinateSystemVlr",
        "GeoKeyDirectoryVlr",
        "GeoAsciiParamsVlr",
        "GeoDoubleParamsVlr",
    ):
        try:
            header.vlrs.extract(crs_vlr_name)
        except IndexError:
            pass

    return header


def write_header_geokeys_from_crs(header: "LasHeader", crs: "CRS") -> "LasHeader":
    header.vlrs.append(GeoAsciiParamsVlr.from_crs(crs))
    header.vlrs.append(GeoKeyDirectoryVlr.from_crs(crs))
    return header


def write_header_scales(header: "LasHeader") -> "LasHeader":
    header.scales = np.array([0.01, 0.01, 0.01])
    return header


def stack_dims(points: "laspy.ScaleAwarePointRecord") -> "np.array":
    x = points.x.scaled_array().copy()
    y = points.y.scaled_array().copy()
    z = points.z.scaled_array().copy()
    return np.stack((x, y, z)).T

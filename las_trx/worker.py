import copy
import math
import multiprocessing
import os
from concurrent import futures
from pathlib import Path
from time import sleep

import laspy
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal as Signal
from laspy import LasHeader
from pyproj import CRS

from csrspy import CSRSTransformer
from las_trx.config import TransformConfig
from las_trx.logger import logger
from las_trx.vlr import GeoAsciiParamsVlr, GeoKeyDirectoryVlr

CHUNK_SIZE = 10_000


class TransformWorker(QThread):
    started = Signal()
    finished = Signal()
    progress = Signal(int)
    success = Signal()
    error = Signal(BaseException)

    def __init__(
        self, config: TransformConfig, input_pattern: str, output_pattern: str
    ):
        super().__init__(parent=None)
        self.config = config
        self.input_pattern = Path(input_pattern)
        self.output_pattern = output_pattern
        self.input_files = [
            f
            for f in self.input_pattern.parent.glob(self.input_pattern.name)
            if f.is_file()
        ]
        self.output_files = [
            Path(output_pattern.format(f.stem)) for f in self.input_files
        ]

        logger.info(f"Found {len(self.input_files)} input files")
        logger.info(f"Transform config: {self.config}")
        logger.info(f"Input CRS\n{self.config.origin.crs.to_wkt(pretty=True)}")
        logger.info(f"Output CRS\n{self.config.destination.crs.to_wkt(pretty=True)}")
        logger.debug(f"Will read points in chunk size of {CHUNK_SIZE}")
        logger.info("Calculating total number of iterations")

        num_workers = min(os.cpu_count(), 61)
        self.pool = futures.ProcessPoolExecutor(max_workers=num_workers)
        self.manager = multiprocessing.Manager()
        self.lock = self.manager.RLock()
        self.current_iter = self.manager.Value("i", 0)
        logger.info(f"CPU process pool size: {num_workers}")

        self.total_iters = 0
        for input_file in self.input_files:
            with laspy.open(str(input_file)) as in_las:
                logger.debug(f"{input_file.name}: {in_las.header.point_count} points")
                self.total_iters += math.ceil(in_las.header.point_count / CHUNK_SIZE)
        logger.info(f"Total iterations until complete: {self.total_iters}")

        self.futs = {}

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
                "Use a format string for the output path to output a file based on the "
                "stem of the corresponding input file. "
                r"e.g. 'C:\\some\path\{}_nad83csrs.laz'"
            )

    def _do_transform(self):
        self.check_file_names()
        config = self.config.to_csrspy().model_dump(exclude_none=True)
        self.futs = {}
        for input_file, output_file in zip(self.input_files, self.output_files):
            if not Path(output_file).suffix:
                output_file += ".laz"
            # logger.info(f"{input_file} -> {output_file}")
            fut = self.pool.submit(
                transform, config, input_file, output_file, self.lock, self.current_iter
            )
            fut.add_done_callback(self.on_process_complete)
            self.futs[fut] = (input_file, output_file)

        while any([f.running() for f in self.futs.keys()]):
            self.progress.emit(self.progress_val)
            sleep(0.1)
        self.progress.emit(self.progress_val)

    def on_process_complete(self, fut: futures.Future):
        input_file, output_file = self.futs[fut]
        err = fut.exception()
        if err is not None:
            logger.error(f"Error transforming {input_file}")
            raise err
        else:
            logger.info(f"{input_file} -> {output_file}")

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

    with laspy.open(str(input_file)) as in_las:
        new_header = copy.deepcopy(in_las.header)
        new_header = clear_header_geokeys(new_header)
        new_header = write_header_geokeys_from_crs(new_header, config.t_crs)
        new_header = write_header_scales(new_header)
        new_header = write_header_offsets(new_header, input_file, transformer)

        laz_backend = laspy.LazBackend.Laszip if output_file.suffix == ".laz" else None
        logger.debug(f"{laz_backend=}")

        with laspy.open(
            str(output_file), mode="w", header=new_header, laz_backend=laz_backend
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
    with laspy.open(str(input_file)) as in_las:
        points = next(in_las.chunk_iterator(CHUNK_SIZE))
        data = stack_dims(points)

        # Convert the coordinates
        data = np.array(list(transformer(data)))

        # Return estimated header offsets as min x,y,z of first batch
        header.offsets = np.min(data, axis=0)
    logger.debug(f"{header.offsets=}")
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
    logger.debug(f"{header.vlrs=}")
    return header


def write_header_scales(header: "LasHeader") -> "LasHeader":
    header.scales = np.array([0.01, 0.01, 0.01])
    logger.debug(f"{header.scales=}")
    return header


def stack_dims(points: "laspy.ScaleAwarePointRecord") -> "np.array":
    x = points.x.scaled_array().copy()
    y = points.y.scaled_array().copy()
    z = points.z.scaled_array().copy()
    return np.stack((x, y, z)).T

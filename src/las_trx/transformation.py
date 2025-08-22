"""Coordinate transformation logic separated from UI threading."""

import copy
import math
import multiprocessing
import os
from collections.abc import Callable, Iterator
from concurrent import futures
from pathlib import Path

import laspy
import numpy as np
from csrspy import CSRSTransformer
from laspy import LasHeader
from laspy.vlrs.known import WktCoordinateSystemVlr
from pyproj import CRS

from las_trx.config import TransformConfig
from las_trx.constants import ProcessingConstants
from las_trx.file_operations import ensure_output_extension, validate_file_paths
from las_trx.logger import logger
from las_trx.vlr import TrxGeoAsciiParamsVlr, TrxGeoKeyDirectoryVlr


class TransformationError(Exception):
    """Base exception for transformation operations."""
    pass


class TransformationManager:
    """Manages coordinate transformation operations without threading concerns."""
    
    def __init__(self, config: TransformConfig, input_pattern: str, output_pattern: str) -> None:
        self.config = config
        self.input_pattern = Path(input_pattern)
        self.output_pattern = output_pattern
        
        # Discover input files
        self.input_files = [
            f for f in self.input_pattern.parent.glob(self.input_pattern.name) 
            if f.is_file()
        ]
        self.output_files = [
            ensure_output_extension(Path(output_pattern.format(f.stem)))
            for f in self.input_files
        ]
        
        # Validate file paths
        validate_file_paths(self.input_files, self.output_files)
        
        # Calculate processing parameters
        self.total_iterations = self._calculate_total_iterations()
        self.num_workers = min(config.max_workers, os.cpu_count() or 1)
        
        # Logging
        logger.info(f"Found {len(self.input_files)} input files")
        logger.info(f"Transform config: {self.config}")
        logger.info(f"Input CRS\\n{self.config.origin.crs.to_wkt(pretty=True)}")
        logger.info(f"Output CRS\\n{self.config.destination.crs.to_wkt(pretty=True)}")
        logger.info(f"Total iterations until complete: {self.total_iterations}")
        logger.info(f"CPU process pool size: {self.num_workers}")
        
    def _calculate_total_iterations(self) -> int:
        """Calculate total number of processing iterations."""
        total = 0
        for input_file in self.input_files:
            with laspy.open(str(input_file)) as las_file:
                point_count = las_file.header.point_count
                chunks = math.ceil(point_count / ProcessingConstants.DEFAULT_CHUNK_SIZE)
                total += chunks
                logger.debug(f"{input_file.name}: {point_count} points, {chunks} chunks")
        return total
    
    def create_progress_tracker(self) -> tuple[multiprocessing.Manager, multiprocessing.RLock, multiprocessing.Value]:
        """Create shared progress tracking objects."""
        manager = multiprocessing.Manager()
        lock = manager.RLock()
        current_iter = manager.Value("i", 0)
        return manager, lock, current_iter
    
    def execute_transformations(
        self, 
        progress_callback: Callable[[int], None] | None = None
    ) -> Iterator[tuple[Path, Path, Exception | None]]:
        """Execute transformations and yield results.
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Yields:
            Tuples of (input_file, output_file, exception_or_none)
        """
        manager, lock, current_iter = self.create_progress_tracker()
        
        with futures.ProcessPoolExecutor(max_workers=self.num_workers) as pool:
            # Submit all transformation jobs
            future_to_files = {}
            for input_file, output_file in zip(self.input_files, self.output_files):
                future = pool.submit(
                    transform_file,
                    self.config,
                    input_file,
                    output_file,
                    lock,
                    current_iter,
                )
                future_to_files[future] = (input_file, output_file)
            
            # Process completed futures
            for future in futures.as_completed(future_to_files):
                input_file, output_file = future_to_files[future]
                exception = future.exception()
                
                if exception:
                    logger.error(f"Error transforming {input_file}: {exception}")
                else:
                    logger.info(f"{input_file} -> {output_file}")
                
                # Call progress callback if provided
                if progress_callback:
                    progress = int(100 * current_iter.value / float(self.total_iterations))
                    progress_callback(progress)
                
                yield input_file, output_file, exception


def transform_file(
    config: TransformConfig,
    input_file: Path,
    output_file: Path,
    lock: multiprocessing.RLock,
    current_iter: multiprocessing.Value,
) -> None:
    """Transform a single LAS file.
    
    Args:
        config: Transformation configuration
        input_file: Input file path
        output_file: Output file path
        lock: Multiprocessing lock for progress tracking
        current_iter: Shared counter for progress tracking
        
    Raises:
        TransformationError: If transformation fails
    """
    try:
        transformer = CSRSTransformer(**config.to_csrspy().model_dump(exclude_none=True))
        
        with laspy.open(str(input_file)) as in_las:
            # Prepare output header
            new_header = prepare_output_header(in_las.header, config, input_file, transformer)
            
            # Determine LAZ backend
            laz_backend = laspy.LazBackend.Laszip if output_file.suffix == ".laz" else None
            logger.debug(f"Using LAZ backend: {laz_backend}")
            
            # Process file in chunks
            with laspy.open(str(output_file), mode="w", header=new_header, laz_backend=laz_backend) as out_las:
                for points in in_las.chunk_iterator(ProcessingConstants.DEFAULT_CHUNK_SIZE):
                    # Transform coordinates
                    data = stack_point_dimensions(points)
                    transformed_data = np.array(list(transformer(data)))
                    
                    # Update point records
                    points.change_scaling(offsets=new_header.offsets, scales=new_header.scales)
                    points.x = transformed_data[:, 0]
                    points.y = transformed_data[:, 1]
                    points.z = transformed_data[:, 2]
                    out_las.write_points(points)
                    
                    # Update progress
                    with lock:
                        current_iter.value += 1
                        
    except Exception as e:
        raise TransformationError(f"Failed to transform {input_file}: {e}") from e


def prepare_output_header(
    input_header: LasHeader, 
    config: TransformConfig,
    input_file: Path, 
    transformer: CSRSTransformer
) -> LasHeader:
    """Prepare output LAS header with proper CRS and scaling."""
    new_header = copy.deepcopy(input_header)
    
    # Clear existing geo keys
    new_header = clear_header_geokeys(new_header)
    
    # Set new CRS information
    new_header = write_header_geokeys_from_crs(new_header, config.destination.crs)
    
    # Set scales and offsets
    new_header = write_header_scales(new_header)
    new_header = write_header_offsets(new_header, input_file, transformer)
    
    return new_header


def clear_header_geokeys(header: LasHeader) -> LasHeader:
    """Remove existing CRS VLRs from header."""
    crs_vlr_names = [
        "WktCoordinateSystemVlr",
        "GeoKeyDirectoryVlr", 
        "GeoAsciiParamsVlr",
        "GeoDoubleParamsVlr",
    ]
    
    for vlr_name in crs_vlr_names:
        try:
            header.vlrs.extract(vlr_name)
        except IndexError:
            pass  # VLR not present
            
    return header


def write_header_geokeys_from_crs(header: LasHeader, crs: CRS) -> LasHeader:
    """Write CRS information to header VLRs."""
    header.vlrs.append(TrxGeoAsciiParamsVlr.from_crs(crs))
    header.vlrs.append(TrxGeoKeyDirectoryVlr.from_crs(crs))
    header.vlrs.append(WktCoordinateSystemVlr(crs.to_wkt()))
    logger.debug(f"Added VLRs: {header.vlrs}")
    return header


def write_header_scales(header: LasHeader) -> LasHeader:
    """Set header coordinate scales."""
    scales = np.array([
        ProcessingConstants.DEFAULT_SCALE_PRECISION,
        ProcessingConstants.DEFAULT_SCALE_PRECISION,
        ProcessingConstants.DEFAULT_SCALE_PRECISION
    ])
    header.scales = scales
    logger.debug(f"Set scales: {header.scales}")
    return header


def write_header_offsets(header: LasHeader, input_file: Path, transformer: CSRSTransformer) -> LasHeader:
    """Calculate and set header coordinate offsets based on first chunk."""
    with laspy.open(str(input_file)) as las_file:
        points = next(las_file.chunk_iterator(ProcessingConstants.DEFAULT_CHUNK_SIZE))
        data = stack_point_dimensions(points)
        
        # Transform coordinates to get representative offset
        transformed_data = np.array(list(transformer(data)))
        header.offsets = np.min(transformed_data, axis=0)
        
    logger.debug(f"Set offsets: {header.offsets}")
    return header


def stack_point_dimensions(points: object) -> np.ndarray:
    """Stack point X, Y, Z coordinates into array for transformation."""
    x = points.x.scaled_array().copy()
    y = points.y.scaled_array().copy()
    z = points.z.scaled_array().copy()
    return np.stack((x, y, z)).T
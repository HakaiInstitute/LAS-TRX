"""Improved worker thread with proper resource management and separation of concerns."""

from time import sleep

from PyQt6.QtCore import QThread, pyqtSignal as Signal

from las_trx.config import TransformConfig
from las_trx.constants import UIConstants
from las_trx.logger import logger
from las_trx.transformation import TransformationError, TransformationManager


class TransformWorker(QThread):
    """Worker thread for coordinate transformations."""

    # Signals
    started = Signal()
    finished = Signal()
    progress = Signal(int)  # Progress percentage (0-100)
    success = Signal()
    error = Signal(Exception)
    file_completed = Signal(str, str)  # input_file, output_file

    def __init__(
        self, config: TransformConfig, input_pattern: str, output_pattern: str, parent: object | None = None
    ) -> None:
        """Initialize the worker thread.

        Args:
            config: Transformation configuration
            input_pattern: Input file pattern (supports wildcards)
            output_pattern: Output file pattern (supports {} formatting)
            parent: Parent QObject
        """
        super().__init__(parent)
        self.config = config
        self.input_pattern = input_pattern
        self.output_pattern = output_pattern
        self.transformation_manager: TransformationManager | None = None
        self._should_stop = False

    def stop_transformation(self) -> None:
        """Request transformation to stop."""
        self._should_stop = True
        logger.info("Stop requested for transformation")

    def run(self) -> None:
        """Execute the transformation in the thread."""
        self.started.emit()

        try:
            # Create transformation manager
            self.transformation_manager = TransformationManager(self.config, self.input_pattern, self.output_pattern)

            # Track if any transformation failed
            has_errors = False
            error_count = 0
            success_count = 0

            # Execute transformations
            for input_file, output_file, exception in self.transformation_manager.execute_transformations(
                progress_callback=self._update_progress
            ):
                # Check if stop was requested
                if self._should_stop:
                    logger.info("Transformation stopped by user request")
                    return

                if exception:
                    has_errors = True
                    error_count += 1
                    logger.error(f"Failed to transform {input_file}: {exception}")
                    self.error.emit(TransformationError(f"Failed to transform {input_file}: {exception}"))
                else:
                    success_count += 1
                    self.file_completed.emit(str(input_file), str(output_file))

                # Small delay to allow UI updates
                sleep(UIConstants.PROGRESS_UPDATE_INTERVAL / 10)

            # Emit final result
            if not has_errors:
                logger.info(f"All {success_count} file(s) transformed successfully")
                self.success.emit()
            else:
                logger.warning(f"Transformation completed with errors: {success_count} succeeded, {error_count} failed")

        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            self.error.emit(e)
        finally:
            self.finished.emit()

    def _update_progress(self, progress: int) -> None:
        """Update progress signal.

        Args:
            progress: Progress percentage (0-100)
        """
        self.progress.emit(progress)

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.isRunning():
            self.stop_transformation()
            # Wait for thread to finish with timeout
            if not self.wait(5000):  # 5 second timeout
                logger.warning("Thread did not finish gracefully, terminating")
                self.terminate()
                self.wait()  # Wait for termination

        self.transformation_manager = None
        logger.debug("Worker cleanup completed")

    def __del__(self) -> None:
        """Destructor to ensure cleanup."""
        self.cleanup()

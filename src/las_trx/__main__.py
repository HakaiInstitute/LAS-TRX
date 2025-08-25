"""Main application entry point using modern architecture."""

import logging
import os
import sys
from multiprocessing import freeze_support
from queue import Queue

from loguru import logger
from PyQt6.QtWidgets import QApplication

from las_trx.main_window import LogDisplayThread, LogWriteStream, MainWindow


def main() -> None:
    freeze_support()

    # Configure logging
    log_msg_queue = Queue()
    log_write_stream = LogWriteStream(log_msg_queue)
    log_handler = logging.StreamHandler(log_write_stream)

    log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
    logging.basicConfig(level=log_level, handlers=[log_handler])

    # Configure loguru to use both the queue and stdout
    logger.add(
        log_write_stream,
        level="DEBUG" if os.getenv("DEBUG") else "INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | <level>{message}</level>",
    )

    # Create application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Setup log display thread
    log_thread = LogDisplayThread(log_msg_queue)
    log_thread.on_msg.connect(window.append_text)
    app.aboutToQuit.connect(log_thread.requestInterruption)
    log_thread.start()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

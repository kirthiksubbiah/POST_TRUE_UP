import os
import sys
import logging
from datetime import datetime


class StdoutToLogger:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        message = message.rstrip()
        if message:
            self.logger.info(message)

    def flush(self):
        pass


def get_logger(name: str, log_dir: str, filename_prefix: str):
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir,
        f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(message)s")

    # IMPORTANT: avoid duplicate handlers
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        #ADD THIS HERE (THIS IS THE CORRECT PLACE)
        sys.stdout = StdoutToLogger(logger)
        sys.stderr = StdoutToLogger(logger)

    return logger

"""
log.py
====================================
The core module for logging instance.
"""

import sys
import logging

LOGGER = logging.getLogger(__package__)
LOGGER.setLevel(logging.DEBUG)

logger_file = logging.FileHandler("logfile.log")
logger_console = logging.StreamHandler(sys.stdout)

logger_file.setLevel(logging.DEBUG)
logger_console.setLevel(logging.INFO)

logger_file.setFormatter(logging.Formatter
    (
    "%(asctime)s - %(module)s- %(funcName)s - %(lineno)d - %(message)s"
    )
)

logger_console.setFormatter(logging.Formatter("%(message)s"))

LOGGER.addHandler(logger_file)
LOGGER.addHandler(logger_console)

logging.getLogger('matplotlib.font_manager').disabled = True




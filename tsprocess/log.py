"""
log.py
====================================
The core module for logging instance.
"""

import sys
import logging

LOGGER = logging.getLogger(__package__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(module)s- %(funcName)s - %(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler("logfile.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.getLogger('matplotlib.font_manager').disabled = True

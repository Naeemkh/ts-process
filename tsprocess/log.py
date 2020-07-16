"""
log.py
====================================
The core module for logging instance.
"""

import logging

LOGGER = logging.getLogger(__package__)
logging.basicConfig(filename="tsprocess_log.log", level=logging.DEBUG,
                    format="%(asctime)s - %(module)s- %(funcName)s - %(lineno)d - %(message)s")
logging.getLogger('matplotlib.font_manager').disabled = True

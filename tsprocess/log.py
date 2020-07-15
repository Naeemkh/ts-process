"""
log.py
====================================
The core module for logging instance.
"""

import logging

LOGGER = logging.getLogger(__package__)
logging.basicConfig(filename="tsprocess_log.log", level=logging.DEBUG,
                    format="%(asctime)s - %(module)s - %(message)s")
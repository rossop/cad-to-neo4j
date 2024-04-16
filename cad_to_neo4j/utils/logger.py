"""
Logger Utilities Module

This module provides utilities for logging operations which can be used for
exploratory and debugging purposes.

Functions:
    - setup_logger: sets up logger with console and file handlers

"""

__all__ = ['setup_logger']

import logging
import os
import sys

def setup_logger(name, level=logging.DEBUG):
    """Sets up a logger with console and file handlers.

    Args:
        name (str): Name of the logger.
        level (int): Logging level.

    Returns:
        tuple: Configured logger, console handler, file handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    log_dir = os.path.expanduser('~/Desktop')
    log_file = os.path.join(log_dir, 'cad_extractor.log')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger, console_handler, file_handler

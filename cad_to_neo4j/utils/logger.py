"""
Logger Utilities Module

This module provides utilities for logging operations which can be used for
exploratory and debugging purposes.

Functions:
    - setup_logger: Sets up logger with console and file handlers.

Decorators:
    - log_function: Logs the entry and exit of a function call.

Logger: 
    - Logger: Configured logger for the application.

Handlers:
    - console_handler: Console handler for the logger.
    - file_handler: File handler for the logger.

"""

__all__ = ['setup_logger', 'log_function', 'Logger', 'console_handler', 'file_handler']

import os
import sys
import logging
from functools import wraps

def setup_logger(name, level=logging.DEBUG):
    """Sets up a logger with console and file handlers.

    Args:
        name (str): Name of the logger.
        level (int): Logging level.

    Returns:
        tuple: Configured logger, console handler, file handler.
    """
    Logger = logging.getLogger(name)
    Logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    Logger.addHandler(console_handler)

    # File Handler
    log_dir = os.path.expanduser('~/Desktop')
    log_file = os.path.join(log_dir, 'cad_extractor.log')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(formatter)
    Logger.addHandler(file_handler)

    return Logger, console_handler, file_handler

Logger, console_handler, file_handler = setup_logger('cad_extractor')

# Logger Decorator
def log_function(func):
    """Decorator to log the entry and exit of a function call.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The wrapped function with logging.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        Logger.info(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        Logger.info(f"{func.__name__} completed")
        return result
    return wrapper

"""
Logger Utilities Module

This module provides utilities for logging operations which can be used for
exploratory and debugging purposes.

Functions:
    - setup_logger: Sets up logger with console and file handlers.
    - clear_all_loggers: Clears all loggers and their handlers.
    - clear_loggers: Clears specific logger and its handlers for a given name.
    - inspect_object : inspect and log an object methods and properties.

Decorators:
    - log_function: Logs the entry and exit of a function call.

Logger: 
    - Logger: Configured logger for the application.

Handlers:
    - console_handler: Console handler for the logger.
    - file_handler: File handler for the logger.

"""

__all__ = ['clear_all_loggers', 'clear_logger', 'setup_logger', 'log_function', 'Logger', 'console_handler', 'file_handler', 'inspect_object']

import os
import sys
import logging
from functools import wraps
from typing import Tuple

def clear_all_loggers():
    """Clears all loggers and their handlers.

    This function retrieves all loggers, including the root logger, and removes
    and closes their handlers. It is useful for ensuring that loggers do not retain
    handlers from previous configurations or executions.
    """
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    loggers.append(logging.getLogger())  # Include the root logger

    for logger in loggers:
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)

def clear_logger(name: str):
    """
    Clears the handlers of the logger with the specified name.

    Args:
        name (str): The name of the logger to clear.
    """
    logger = logging.getLogger(name)
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)


def setup_logger(name: str,
                 level: int = logging.DEBUG, 
                 log_dir: str = '~/Desktop', 
                 log_file: str = 'cad_to_graph.log'
                 ) -> Tuple[logging.Logger, logging.Handler, logging.Handler]:
    """Sets up a logger with console and file handlers.

    Args:
        name (str): Name of the logger.
        level (int): Logging level.
        log_dir (str): Directory where the log file will be saved.
        log_file (str): Name of the log file.

    Returns:
        tuple: Configured logger, console handler, file handler.
    """
    clear_logger(name)  # Clear any existing handlers for the logger

    Logger = logging.getLogger(name)
    Logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    Logger.addHandler(console_handler)

    # File Handler
    log_dir = os.path.expanduser(log_dir)
    log_file_path = os.path.join(log_dir, log_file)
    file_handler = logging.FileHandler(log_file_path, mode='a')
    file_handler.setFormatter(formatter)
    Logger.addHandler(file_handler)

    return Logger, console_handler, file_handler

Logger, console_handler, file_handler = setup_logger('cad_to_graph')

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


def inspect_object(obj):
    """Inspects an object and logs its properties and methods.

    Args:
        obj: The object to inspect.
    """
    Logger.debug(f"_______________________________")
    class_name = obj.__class__.__name__
    Logger.debug(f"Inspecting {class_name} object:")
    
    for attr_name in dir(obj):
        if not attr_name.startswith('__'):
            try:
                attr_value = getattr(obj, attr_name)
                if callable(attr_value):
                    Logger.debug(f"  Method: {attr_name}")
                else:
                    Logger.debug(f"  Property: {attr_name} = {attr_value}")
            except:
                Logger.debug(f"  Unable to access: {attr_name}")
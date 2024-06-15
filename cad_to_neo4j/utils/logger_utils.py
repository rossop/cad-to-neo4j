"""
Logger Utilities Module

This module provides utilities for logging operations which can be used for
exploratory and debugging purposes. It includes a LoggerUtility class that
facilitates the setup and management of loggers and provides decorators
for logging function calls and errors.

Classes:
    - LoggerUtility: A utility class for setting up and managing logging operations.

Methods:
    - clear_all_loggers: Clears all loggers and their handlers.
    - clear_logger: Clears specific logger and its handlers.
    - setup_logger: Sets up logger with console and file handlers.
    - inspect_object: Inspects and logs an object's methods and properties.
    - log_function: Logs the entry and exit of a function call.
    - log_debug: Logs the entry and exit of a function call at the DEBUG level.
    - log_error: Logs the entry and exit of a function call at the ERROR level.
    - update_file_handler: Updates the file handler with the new log directory or log file.

Attributes:
    - Logger: Configured logger for the application.
    - console_handler: Console handler for the logger.
    - file_handler: File handler for the logger.

"""

__all__ = ['LoggerUtility', 'logger_utility']

import os
import sys
import logging
from functools import wraps
from typing import Tuple
import traceback

class LoggerUtility(object):
    """
    A utility class for setting up and managing logging operations, 
    useful for exploratory and debugging purposes.

    Attributes:
        name (str): The name of the logger.
        level (int): The logging level.
        log_dir (str): Directory where the log file will be saved.
        log_file (str): Name of the log file.

    Methods:
        clear_all_loggers(): Clears all loggers and their handlers.
        clear_logger(): Clears the handlers of the logger with the specified name.
        setup_logger(): Sets up a logger with console and file handlers.
        __call__(func): Allows the class instance to be used as a decorator.
        log_function(func): Logs the entry and exit of a function call.
        log_debug(func): Logs the entry and exit of a function call at the DEBUG level.
        log_error(func): Logs the entry and exit of a function call at the ERROR level.
        inspect_object(obj): Inspects an object and logs its properties and methods.
    """

    def __init__(
            self, 
            name: str, 
            level: int = logging.INFO, 
            log_dir: str = '~/Desktop', 
            log_file: str = 'cad_to_graph.log'
            ) -> None:
        """
        Initializes the LoggerUtility with specified configurations.

        Args:
            name (str): Name of the logger.
            level (int): Logging level.
            log_dir (str): Directory where the log file will be saved.
            log_file (str): Name of the log file.
        """
        self.name = name
        self._level =level
        self._log_dir = log_dir # Initialise to None
        self._log_file = log_file # Initialise to None
        self.logger, self.console_handler, self.file_handler = self.setup_logger()
    
    def __str__(self):
        return f"LoggerUtility(name={self.name}, level={self._level}, log_dir={self._log_dir}, log_file={self._log_file})"

    def __repr__(self):
        return self.__str__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.clear_logger()

    def __call__(self, func):
        """Allows the class instance to be used as a decorator for logging function calls."""
        return self.log_function(func)
    
    def __del__(self):
        """Destructor to clean up logger and its handlers."""
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("Stopping Script and cleaning up logger.")
            if hasattr(self, 'console_handler') and self.console_handler:
                self.logger.removeHandler(self.console_handler)
                self.console_handler.close()
                self.console_handler = None
            if hasattr(self, 'file_handler') and self.file_handler:
                self.logger.removeHandler(self.file_handler)
                self.file_handler.close()
                self.file_handler = None
            self.logger = None

    def clear_all_loggers(self):
        """
        Clears all loggers and their handlers.

        This method retrieves all loggers, including the root logger, and removes
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

    def clear_logger(self):
        """
        Clears the handlers of the logger with the specified name.
        """
        logger = logging.getLogger(self.name)
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)

    def setup_logger(self) -> Tuple[logging.Logger, logging.Handler, logging.Handler]:
        """
        Sets up a logger with console and file handlers.

        Returns:
            tuple: Configured logger, console handler, file handler.
        """
        self.clear_logger()  # Clear any existing handlers for the logger

        logger = logging.getLogger(self.name)
        logger.setLevel(self._level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler
        log_file_path = os.path.expanduser(os.path.join(self._log_dir, self._log_file))
        file_handler = logging.FileHandler(log_file_path, mode='a')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger, console_handler, file_handler
    
    @property
    def log_file(self):
        """Gets the current log file name."""
        return self._log_file

    @log_file.setter
    def log_file(self, value: str):
        """Sets the log file name and updates the file handler."""
        self._log_file = value
        self.update_file_handler()

    @property
    def level(self):
        """Gets the current logging level."""
        return self._level

    @level.setter
    def level(self, value: int):
        """Sets the logging level and updates the logger."""
        self._level = value
        self.logger.setLevel(self._level)

    @level.deleter
    def level(self):
        """Resets the logging level to default (INFO) and updates the logger."""
        self._level = logging.INFO
        self.logger.setLevel(self._level)

    def update_file_handler(self):
        """Updates the file handler with the new log directory or log file."""
        if self._log_dir and self._log_file:
            self.clear_logger()
            log_file_path = os.path.join(self._log_dir, self._log_file)
            file_handler = logging.FileHandler(log_file_path, mode='a')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(self.console_handler)
            self.logger.addHandler(file_handler)

    # decorator
    def log_function(self, func):
        """Decorator to log the entry and exit of a function call."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.info(f"Calling {func.__name__}")
            result = func(*args, **kwargs)
            self.logger.info(f"{func.__name__} completed")
            return result
        return wrapper

    # decorator
    def log_debug(self, func):
        """Decorator to log the entry and exit of a function call at the DEBUG level."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.debug(f"Calling {func.__name__}")
            result = func(*args, **kwargs)
            self.logger.debug(f"{func.__name__} completed")
            return result
        return wrapper
    
    # decorator
    def log_error(self, func):
        """Decorator to log the entry and exit of a function call at the ERROR level."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.logger.info(f"Calling {func.__name__}")
                result = func(*args, **kwargs)
                self.logger.info(f"{func.__name__} completed")
                return result
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {e}")
                raise
        return wrapper

    def inspect_object(self, obj):
        """Inspects an object and logs its properties and methods.

        Args:
            obj: The object to inspect.
        """
        self.logger.debug(f"_______________________________")
        class_name = obj.__class__.__name__
        self.logger.debug(f"Inspecting {class_name} object:")
        
        for attr_name in dir(obj):
            if not attr_name.startswith('__'):
                try:
                    attr_value = getattr(obj, attr_name)
                    if callable(attr_value):
                        self.logger.debug(f"  Method: {attr_name}")
                    else:
                        self.logger.debug(f"  Property: {attr_name} = {attr_value}")
                except:
                    self.logger.debug(f"  Unable to access: {attr_name}")

# Create an instance of LoggerUtility
logger_utility = LoggerUtility('cad_to_graph', level=logging.DEBUG)

if __name__ == '__main__':
    # Create an instance of LoggerUtility
    logger_utility = LoggerUtility('cad_to_graph')

    # Example function using the logger utility
    @logger_utility.log_function
    def sample_function():
        print("This is a sample function")

    @logger_utility.log_error
    def function_with_error_handling():
        try:
            # Some logic that may raise an error
            pass
        except Exception as e:
            logger_utility.logger.error(f'Error: {e}\n{traceback.format_exc()}')
            raise

    # Example usage of property methods
    logger_utility.log_dir = '~/NewLogDirectory'
    logger_utility.log_file = 'new_log_file.log'
    logger_utility.level = logging.WARNING  # Change the logging level

    sample_function()
    function_with_error_handling()
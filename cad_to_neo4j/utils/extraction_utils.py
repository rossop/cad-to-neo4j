"""
Extraction Utilities.

This module provides utility functions and decorators to handle errors and
simplify operations during extraction processes in the project. It includes
functions for retrieving nested attributes from objects and error handling in
extraction methods.

Functions and Decorators:
-------------------------
- `nested_getattr`: Recursively get nested attributes from an object.
- `nested_hasattr`: Recursively check if nested attributes exist on an object.
- `helper_extraction_error`: A decorator to handle errors during extraction.
"""
from functools import wraps
import traceback
from typing import Optional, Any

__all__ = ['nested_getattr', 'nested_hasattr', 'helper_extraction_error']


def nested_getattr(
        obj: object, attr: str, default: Optional[Any] = None) -> Any:
    """
    Recursively get attributes from an object.

    Args:
        obj: The object from which to get the attribute.
        attr (str): A string representing the nested attribute, separated by
            dots.
        default: The default value to return if any attribute in the chain
            does not exist.

    Returns:
        The value of the nested attribute, or the default value if any
        attribute in the chain does not exist.

    Example:
        class InnerClass:
            def __init__(self):
                self.inner_attr = 'inner value'

        class OuterClass:
            def __init__(self):
                self.outer_attr = InnerClass()

        outer_instance = OuterClass() value = nested_getattr(outer_instance,
        'outer_attr.inner_attr', 'default value') print(value)  # Output: inner
        value
    """
    try:
        for key in attr.split('.'):
            if hasattr(obj, key):
                obj = getattr(obj, key)
            else:
                return default
        return obj
    except AttributeError:
        return default


def nested_hasattr(obj, attr: str) -> bool:
    """
    Recursively check if the nested attribute exists.

    Args:
        obj: The object to check.
        attr: A string representing the nested attribute, separated by dots.

    Returns:
        bool: True if the nested attribute exists, False otherwise.
    """
    try:
        for key in attr.split('.'):
            if not hasattr(obj, key):
                return False
            obj = getattr(obj, key)
        return True
    except AttributeError:
        return False


def helper_extraction_error(func):
    """
    A decorator to handle errors during extraction processes.

    Logs errors and provides traceback information for extraction-related
    methods, ensuring that any exceptions are caught and logged in a
    consistent manner.

    Args:
        func (function): The function to wrap and monitor for exceptions.

    Returns:
        function: The wrapped function with enhanced error handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        instance = args[0]  # Assumes the first argument is the class instance
        logger = instance.logger
        extractor_name = instance.__class__.__name__  # Name of the extractor
        method_name = func.__name__  # Name of the function being wrapped

        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = (
                f"Error in extractor '{extractor_name}', "
                f"method '{method_name}':\n"
                f"Exception: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            logger.error(error_message)
            return None
    return wrapper

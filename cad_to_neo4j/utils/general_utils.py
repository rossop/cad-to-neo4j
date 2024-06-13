"""General utility functions.

This module provides general utility functions that can be used across
various parts of the project. These functions are designed to simplify 
common tasks and ensure code reusability.
"""
from typing import Optional, Any

__all__ = ['nested_getattr', 'nested_hasattr']

def nested_getattr(obj: object, attr: str, default: Optional[Any] = None) -> Any:
    """
    Recursively get attributes from an object.

    Args:
        obj: The object from which to get the attribute.
        attr (str): A string representing the nested attribute, separated by dots.
        default: The default value to return if any attribute in the chain does not exist.

    Returns:
        The value of the nested attribute, or the default value if any attribute in the chain does not exist.

    Example:
        class InnerClass:
            def __init__(self):
                self.inner_attr = 'inner value'

        class OuterClass:
            def __init__(self):
                self.outer_attr = InnerClass()

        outer_instance = OuterClass()
        value = nested_getattr(outer_instance, 'outer_attr.inner_attr', 'default value')
        print(value)  # Output: inner value
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
"""General utility functions.

This module provides general utility functions that can be used across
various parts of the project. These functions are designed to simplify 
common tasks and ensure code reusability.
"""

__all__ = ['nested_getattr']

def nested_getattr(obj, attr, default=None):
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
            obj = getattr(obj, key)
        return obj
    except AttributeError:
        return default
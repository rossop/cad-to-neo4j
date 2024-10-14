"""
Cypher Query Error Handling Utilities.

This module provides a utility decorator to handle errors during the execution
of Cypher queries. It captures exceptions, logs detailed error messages, and
ensures that any Cypher query failures are managed without boilerplate code.

Functions and Decorators:
-------------------------
- `helper_cypher_error`: A decorator to handle errors during Cypher query
    execution.
"""

from functools import wraps
import traceback

__all__ = ['helper_cypher_error']


def helper_cypher_error(func):
    """
    A decorator to handle errors during the execution of Cypher queries.

    Logs errors and provides traceback information during Cypher query
    execution, ensuring errors are caught, logged, and query execution
    failures do not propagate.

    Args:
        func (function): The function to wrap and monitor for exceptions.

    Returns:
        function: The wrapped function with enhanced error handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        instance = args[0]  # Assumes the first argument is the class instance
        logger = instance.logger
        transformer_name = instance.__class__.__name__  # transforme's name
        query_name = func.__name__  # Name of the function being wrapped

        try:
            return func(*args, **kwargs)
        except Exception as e:
            query = kwargs.get('query', 'No query provided')
            error_message = (
                f"Error in transformer '{transformer_name}', "
                f"query '{query_name}':\n"
                f"Query: {query}\n"
                f"Exception: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            logger.error(error_message)
            return []
    return wrapper

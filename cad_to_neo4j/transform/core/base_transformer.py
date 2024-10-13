"""
Base Transformer Module

This module provides the base class for all transformation strategies.

Classes:
    - BaseTransformer: A base class for transformation strategies.
"""

import logging


class BaseTransformer:
    """
    BaseTransformer

    A base class for transformation strategies.

    Attributes:
        logger (logging.Logger): The logger for logging messages and errors.

    Methods:
        __init__(logger): Initialises the transformer with an optional logger.
        transform(execute_query): The transform method to be overridden by
        subclasses.
    """
    def __init__(self, logger: logging.Logger = None):
        """
        Initialises the BaseTransformer with an optional logger.

        Args:
            logger (logging.Logger, optional): The logger for logging messages
            and errors. Defaults to None.
        """
        self.logger = logger if logger else logging.getLogger(__name__)

    def transform(self, execute_query):
        """
        The transform method to be overridden by subclasses.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: A dictionary containing the results of all transformations.
        """
        raise NotImplementedError("Subclasses should implement this method")

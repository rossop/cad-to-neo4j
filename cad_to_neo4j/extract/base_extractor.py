"""
Base Extractor Module

This module provides a base class for extracting basic properties from CAD
objects.

Classes:
    - BaseExtractor: Extracts name, type, and id token from a CAD object.
"""

import logging
import traceback

from typing import Optional, Dict, List, Any, Callable
import inspect

import adsk.core

from ..utils.general_utils import nested_getattr, nested_hasattr
from ..utils.logger_utils import logger_utility

__all__ = ['BaseExtractor']


class BaseExtractor(object):
    """Base class for extracting basic properties from CAD objects."""

    def __init__(self, obj: adsk.core.Base):
        """Initialises the BaseExtractor with a CAD object.

        Args:
            obj: The CAD object to extract information from.
        """
        self._obj = obj
        self._type = None  # Initialise the type to None
        self.logger: logging.Logger = logger_utility.logger

    @staticmethod
    def safe_extraction(func: Callable) -> Callable:
        """
        A decorator to handle safe extraction of properties.
        It catches AttributeError, RuntimeError, ValueError, logs them
        using _log_extraction_error, and returns None in case of failure.
        """
        def wrapper(self, *args, **kwargs) -> Optional[Any]:
            try:
                # Try executing the original function
                return func(self, *args, **kwargs)  # pass self to the function
            except AttributeError as e:
                # Log attribute errors (e.g., missing attributes)
                attribute_error_msg = \
                    f"AttributeError occurred in {func.__name__}: {e}"
                self.logger.error(attribute_error_msg)
                self.logger.error("Traceback: %s", traceback.format_exc())
            except RuntimeError as e:
                # Log runtime errors (e.g., issues during execution)
                runtime_error_msg = \
                    f"RuntimeError occurred in {func.__name__}: {e}"
                self.logger.error(runtime_error_msg)
                self.logger.error("Traceback: %s", traceback.format_exc())
            except ValueError as e:
                # Log value errors (e.g., unsupported types)
                value_error_msg = \
                    f"ValueError occurred in {func.__name__}: {e}"
                self.logger.error(value_error_msg)
                self.logger.error("Traceback: %s", traceback.format_exc())
            except Exception as e:
                # Catch-all for any other exceptions
                unexp_error_msg = \
                    f"Unexpected error occurred in {func.__name__}: {e}"
                self.logger.error(unexp_error_msg)
                self.logger.error("Traceback: %s", traceback.format_exc())
            return None
        return wrapper

    def extract_info(self) -> Dict[str, Optional[str]]:
        """Extracts basic information (name, type, id token) of the CAD object.

        Returns:
            dict: A dictionary containing the name, type, and id token.
        """
        return {
            'name': self.name,
            'type': self.type,
            'entityToken': self.entity_token,
            'timelineIndex': self.timeline_index,
        }

    @property
    @safe_extraction
    def name(self) -> Optional[str]:
        """Extracts the name of the CAD object.

        Returns:
            str: The name of the CAD object, or None if not available.
        """
        if hasattr(self._obj, 'name'):
            return getattr(self._obj, 'name', None)
        return None

    @property
    def type(self) -> str:
        """Extracts the type of the CAD object.

        Returns:
            str: The type of the CAD object.
        """
        object_type: str = self._get_class_hierarchy()
        if object_type is not None:
            return object_type
        else:
            return ["Unknown"]

    @property
    @safe_extraction
    def entity_token(self) -> Optional[str]:
        """Extracts the id token of the CAD object.

        Returns:
            str: The id token of the CAD object, or None if not available.
        """
        if hasattr(self._obj, 'entityToken'):
            return getattr(self._obj, 'entityToken', None)

    @property
    @safe_extraction
    def timeline_index(self) -> Optional[int]:
        """Extracts the timeline index of the Sketch object.

        Returns:
            int: The timeline index of the Sketch object, or None if not
            available.
        """
        return nested_getattr(self._obj, 'timelineObject.index', None)

    @safe_extraction
    def _get_class_hierarchy(self) -> List[str]:
        """Gets the class hierarchy of the CAD object.

        Returns:
            List[str]: A list of class names in the class hierarchy
        """
        class_hierarchy = inspect.getmro(self._obj.__class__)
        # Simplify class names using map
        simplified_class_names = map(
            lambda cls: self._simplify_class_name(cls.__name__) if
            '::' in cls.__name__ else cls.__name__,
            class_hierarchy)

        # Filter out 'Base' and 'object' using filter
        filtered_class_names = filter(
            lambda name: name not in ('Base', 'object'),
            simplified_class_names
        )

        # Convert the filter object to a list and return it
        return list(filtered_class_names)

    def _simplify_class_name(self, class_name: str) -> str:
        """Simplifies the class name by splitting by '::' and taking the last
        part if applicable.

        Args:
            class_name: The original class name.

        Returns:
            str: The simplified class name.
        """
        parts = class_name.split('::')
        return parts[-1] if len(parts) > 1 else class_name

    @safe_extraction
    def extract_collection_tokens(self, attribute, id_attr='entityToken'):
        """Extracts a list of IDs from a given attribute."""
        collection = getattr(self._obj, attribute, [])
        if hasattr(collection, "__iter__"):
            ids = [getattr(item, id_attr, None) for item in collection]
            return ids
        return []

    def get_first_valid_attribute(self,
                                  attributes: List[str]) -> Optional[Any]:
        """
        Attempt to retrieve the first valid attribute from a list of
        possible attributes.

        Args:
            attributes (List[str]): A list of attribute names to attempt to
            retrieve.

        Returns:
            Optional[Any]: The value of the first valid attribute found, or
                None if none are found.
        """
        for attr in attributes:
            if nested_hasattr(self._obj, attr):
                return nested_getattr(self._obj, attr, None)
        return None

    def _log_extraction_error(self,
                              error: Exception,
                              field: Optional[str] = None) -> None:
        """
        Logs errors encountered during extraction. If a field name is provided,
        it will log it, otherwise it infers the calling property's name
        automatically.

        Args:
            error (Exception): The exception to log.
            field (Optional[str]): The name of the field (optional). If not
                provided, it will be inferred.
        """
        # If no field is provided, infer it from the caller using inspect
        if field is None:
            current_frame = inspect.currentframe()
            caller_frame = current_frame.f_back
            field = caller_frame.f_code.co_name

        # Log the error
        error_message = (
            f"Error extracting {field}: {error}\n"
            f"{traceback.format_exc()}"
        )
        self.logger.error(error_message)

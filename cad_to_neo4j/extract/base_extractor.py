"""
Base Extractor Module

This module provides a base class for extracting basic properties from CAD objects.

Classes:
    - BaseExtractor: Extracts name, type, and id token from a CAD object.
"""

from adsk.core import Base # TODO fix import
from typing import Optional, Dict, List
from ..utils.logger_utils import Logger
import traceback
import inspect

__all__ = ['BaseExtractor']

class BaseExtractor(object):
    """Base class for extracting basic properties from CAD objects."""

    def __init__(self, obj: Base):
        """Initialises the BaseExtractor with a CAD object.

        Args:
            obj: The CAD object to extract information from.
        """
        self._obj = obj
        self._type = None  # Initialise the type to None
        self.logger = Logger

    @property
    def name(self) -> Optional[str]:
        """Extracts the name of the CAD object.

        Returns:
            str: The name of the CAD object, or None if not available.
        """
        try:
            if hasattr(self._obj, 'name'):
                return getattr(self._obj, 'name', None)
            return None
        except AttributeError as e:
            self.logger.error(f'Error : {e}\n{traceback.format_exc()}')
            return None

    @property
    def type(self) -> str:
        """Extracts the type of the CAD object.

        Returns:
            str: The type of the CAD object.
        """
        try:
            return self._get_class_hierarchy()
        except AttributeError as e:
            self.logger.error(f'Error : {e}\n{traceback.format_exc()}')
            return ["Unknown"]

    @property
    def id_token(self) -> Optional[str]:
        """Extracts the id token of the CAD object.

        Returns:
            str: The id token of the CAD object, or None if not available.
        """
        try:
            if hasattr(self._obj, 'entityToken'):
                return getattr(self._obj, 'entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error : {e}\n{traceback.format_exc()}')
            return None
        
    def _get_class_hierarchy(self) -> List[str]:
        """Gets the class hierarchy of the CAD object.
        
        Returns:
            List[str]: A list of class names in the class hierarchy
        """
        try:
            class_hierarchy = inspect.getmro(self._obj.__class__)
            # Simplify class names using map
            simplified_class_names = map(
                lambda cls: self._simplify_class_name(cls.__name__) if '::' in cls.__name__ else cls.__name__,
                class_hierarchy
            )
            
            # Filter out 'Base' and 'object' using filter
            filtered_class_names = filter(
                lambda name: name not in ('Base', 'object'),
                simplified_class_names
            )
            
            # Convert the filter object to a list and return it
            return list(filtered_class_names)
        except Exception as e:
            self.logger.error(f'Error : {e}\n{traceback.format_exc()}')
            return ['Unknown']

    def _simplify_class_name(self, class_name: str) -> str:
        """Simplifies the class name by splitting by '::' and taking the last part if applicable.

        Args:
            class_name: The original class name.

        Returns:
            str: The simplified class name.
        """
        parts = class_name.split('::')
        return parts[-1] if len(parts) > 1 else class_name

    def extract_info(self) -> Dict[str, Optional[str]]:
        """Extracts basic information (name, type, id token) of the CAD object.

        Returns:
            dict: A dictionary containing the name, type, and id token.
        """
        return {
            'name': self.name,
            'type': self.type,
            'id_token': self.id_token,
        }
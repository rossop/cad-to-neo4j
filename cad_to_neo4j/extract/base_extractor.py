"""
Base Extractor Module

This module provides a base class for extracting basic properties from CAD objects.

Classes:
    - BaseExtractor: Extracts name, type, and id token from a CAD object.
"""

from adsk.core import Base # TODO fix import
from typing import Optional, Dict

class BaseExtractor(object):
    """Base class for extracting basic properties from CAD objects."""

    def __init__(self, obj: Base):
        """Initialises the BaseExtractor with a CAD object.

        Args:
            obj: The CAD object to extract information from.
        """
        self._obj = obj
        self._type = None  # Initialise the type to None

    @property
    def name(self) -> Optional[str]:
        """Extracts the name of the CAD object.

        Returns:
            str: The name of the CAD object, or None if not available.
        """
        try:
            return self._obj.name
        except AttributeError:
            return None

    @property
    def type(self) -> str:
        """Extracts the type of the CAD object.

        Returns:
            str: The type of the CAD object.
        """
        if self._type is None:
            self._type = self._obj.classType()
        return self._type

    @property
    def id_token(self) -> Optional[str]:
        """Extracts the id token of the CAD object.

        Returns:
            str: The id token of the CAD object, or None if not available.
        """
        try:
            return self._obj.entityToken
        except AttributeError:
            return None

    def extract_basic_info(self) -> Dict[str, Optional[str]]:
        """Extracts basic information (name, type, id token) of the CAD object.

        Returns:
            dict: A dictionary containing the name, type, and id token.
        """
        return {
            'name': self.name,
            'type': self.type,
            'id_token': self.id_token,
        }
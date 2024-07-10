"""
BRep Shell Extractor Module

This module provides an extractor class for extracting information from 
BRepShell objects, including their parent lump, parent body, and other 
properties.

Classes:
    - BRepShellExtractor: Extractor for BRepShell objects.
"""
from typing import Optional, Dict, List, Any
import adsk.core
import adsk.fusion # TODO standardise this import for 
from .brep_entity_extractor import BRepEntityExtractor

__all__ = ['BRepShellExtractor']

class BRepShellExtractor(BRepEntityExtractor):
    """
    Extractor for BRepShell objects.

    This class provides methods to extract various properties from a BRepShell object.

    Attributes:
        shell (adsk.fusion.BRepShell): The BRep shell object to extract data from.
    """

    def __init__(self, obj: adsk.fusion.BRepShell):
        """Initializes the BRepShellExtractor with a BRepShell object.

        Args:
            obj: The BRep shell object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the BRepShell element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        brep_shell_info = {
            'lump': self.lump,
            'isClosed': self.isClosed,
            'isVoid': self.isVoid,
            # 'wire': self.wire,
        }

        return {**base_info, **brep_shell_info}

    @property
    def lump(self) -> Optional[str]:
        """
        Returns the parent lump of this shell.

        Returns:
            Optional[str]: Entity token of the parent lump.
        """
        try:
            lump = getattr(self._obj, 'lump', None)
            return getattr(lump, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting lump: {e}")
            return None

    @property
    def body(self) -> Optional[str]:
        """
        Returns the parent body of the shell.

        Returns:
            Optional[str]: Entity token of the parent body.
        """
        try:
            lump = getattr(self._obj, 'nody', None)
            return getattr(lump, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting body: {e}")
            return None

    @property
    def isClosed(self) -> Optional[bool]:
        """
        Returns true if this shell is closed.

        Returns:
            Optional[bool]: True if the shell is closed, False otherwise.
        """
        try:
            return getattr(self._obj, 'isClosed', None)
        except Exception as e:
            self.logger.error(f"Error extracting isClosed: {e}")
            return None

    @property
    def isVoid(self) -> Optional[bool]:
        """
        Returns true if the faces of this shell bound a void or an empty space within an outer shell.

        Returns:
            Optional[bool]: True if the shell is void, False otherwise.
        """
        try:
            return getattr(self._obj, 'isVoid', None)
        except Exception as e:
            self.logger.error(f"Error extracting isVoid: {e}")
            return None
        
    @property
    def wire(self) -> Optional[str]:
        """
        Returns the wire body, if any, that exists in this shell. Returns null if the shell doesn't have a wire body.

        Returns:
            Optional[str]: Entity token of the wire body.
        """
        try:
            wire = getattr(self._obj, 'wire', None)
            return getattr(wire, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting wire: {e}")
            return None


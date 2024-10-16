"""
Sketch Angular Dimension Extractor Module

This module provides an extractor class for extracting information from SketchAngularDimension objects.

Classes:
    - SketchAngularDimensionExtractor: Extractor for SketchAngularDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchAngularDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.extraction_utils import nested_getattr

__all__ = ['SketchAngularDimensionExtractor']

class SketchAngularDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchAngularDimension objects."""

    def __init__(self, obj: SketchAngularDimension):
        """
        Initialize the extractor with the SketchAngularDimension element.

        Args:
            obj (SketchAngularDimension): The SketchAngularDimension object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchAngularDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'lineOne': self.lineOne,
            'lineTwo': self.lineTwo,
        }

        return {**basic_info, **dimension_info}

    @property
    def lineOne(self) -> Optional[str]:
        """
        Extract the first line being constrained.

        Returns:
            str: The entity token of the first line, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'lineOne.entityToken', None)
        except AttributeError:
            return None

    @property
    def lineTwo(self) -> Optional[str]:
        """
        Extract the second line being constrained.

        Returns:
            str: The entity token of the second line, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'lineTwo.entityToken', None)
        except AttributeError:
            return None

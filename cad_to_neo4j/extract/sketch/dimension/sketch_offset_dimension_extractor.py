"""
Sketch Offset Dimension Extractor Module

This module provides an extractor class for extracting information from SketchOffsetDimension objects.

Classes:
    - SketchOffsetDimensionExtractor: Extractor for SketchOffsetDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchOffsetDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchOffsetDimensionExtractor']

class SketchOffsetDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchOffsetDimension objects."""

    def __init__(self, obj: SketchOffsetDimension):
        """
        Initialize the extractor with the SketchOffsetDimension element.

        Args:
            obj (SketchOffsetDimension): The SketchOffsetDimension object to extract information from.
        """
        super().__init__(obj)

    @property
    def line(self) -> Optional[str]:
        """
        Extract the first line being constrained.

        Returns:
            str: The entity token of the first line, or None if not available.
        """
        try:
            return nested_getattr(self._obj, 'line.entityToken', None)
        except AttributeError:
            return None

    @property
    def entityTwo(self) -> Optional[str]:
        """
        Extract the second entity being constrained.

        Returns:
            str: The entity token of the second entity, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'entityTwo.entityToken', None)
        except AttributeError:
            return None

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchOffsetDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'line': self.line,
            'entityTwo': self.entityTwo,
        }

        return {**basic_info, **dimension_info}

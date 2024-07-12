"""
Sketch Concentric Circle Dimension Extractor Module

This module provides an extractor class for extracting information from SketchConcentricCircleDimension objects.

Classes:
    - SketchConcentricCircleDimensionExtractor: Extractor for SketchConcentricCircleDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchConcentricCircleDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchConcentricCircleDimensionExtractor']

class SketchConcentricCircleDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchConcentricCircleDimension objects."""

    def __init__(self, obj: SketchConcentricCircleDimension):
        """
        Initialize the extractor with the SketchConcentricCircleDimension element.

        Args:
            obj (SketchConcentricCircleDimension): The SketchConcentricCircleDimension object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchConcentricCircleDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'circleOne': self.circleOne,
            'circleTwo': self.circleTwo,
        }

        return {**basic_info, **dimension_info}

    @property
    def circleOne(self) -> Optional[str]:
        """
        Extract the first concentric circle or arc.

        Returns:
            str: The entity token of the first concentric circle or arc, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'circleOne.entityToken', None)
        except AttributeError:
            return None

    @property
    def circleTwo(self) -> Optional[str]:
        """
        Extract the second concentric circle or arc.

        Returns:
            str: The entity token of the second concentric circle or arc, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'circleTwo.entityToken', None)
        except AttributeError:
            return None

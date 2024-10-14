"""
Sketch Tangent Distance Dimension Extractor Module

This module provides an extractor class for extracting information from SketchTangentDistanceDimension objects.

Classes:
    - SketchTangentDistanceDimensionExtractor: Extractor for SketchTangentDistanceDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchTangentDistanceDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.extraction_utils import nested_getattr

__all__ = ['SketchTangentDistanceDimensionExtractor']

class SketchTangentDistanceDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchTangentDistanceDimension objects."""

    def __init__(self, obj: SketchTangentDistanceDimension):
        """
        Initialize the extractor with the SketchTangentDistanceDimension element.

        Args:
            obj (SketchTangentDistanceDimension): The SketchTangentDistanceDimension object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchTangentDistanceDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'entityOne': self.entityOne,
            'circleOrArc': self.circleOrArc,
        }

        return {**basic_info, **dimension_info}
    
    @property
    def entityOne(self) -> Optional[str]:
        """
        Extract the first entity being constrained.

        Returns:
            str: The entity token of the first entity, or None if not available.
        """
        try:
            return nested_getattr(self._obj, 'entityOne.entityToken', None)
        except AttributeError:
            return None

    @property
    def circleOrArc(self) -> Optional[str]:
        """
        Extract the second entity being constrained.

        Returns:
            str: The entity token of the circle or arc, or None if not available.
        """
        try:
            return nested_getattr(self._obj, 'circleOrArc.entityToken', None)
        except AttributeError:
            return None
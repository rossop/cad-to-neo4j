"""
Sketch Distance Between Point and Surface Dimension Extractor Module

This module provides an extractor class for extracting information from SketchDistanceBetweenPointAndSurfaceDimension objects.

Classes:
    - SketchDistanceBetweenPointAndSurfaceDimensionExtractor: Extractor for SketchDistanceBetweenPointAndSurfaceDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchDistanceBetweenPointAndSurfaceDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchDistanceBetweenPointAndSurfaceDimensionExtractor']

class SketchDistanceBetweenPointAndSurfaceDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchDistanceBetweenPointAndSurfaceDimension objects."""

    def __init__(self, obj: SketchDistanceBetweenPointAndSurfaceDimension):
        """
        Initialize the extractor with the SketchDistanceBetweenPointAndSurfaceDimension element.

        Args:
            obj (SketchDistanceBetweenPointAndSurfaceDimension): The SketchDistanceBetweenPointAndSurfaceDimension object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchDistanceBetweenPointAndSurfaceDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'point': self.point,
            'surface': self.surface,
        }

        return {**basic_info, **dimension_info}

    @property
    def point(self) -> Optional[str]:
        """
        Extract the sketch point being constrained.

        Returns:
            str: The entity token of the sketch point, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'point.entityToken', None)
        except AttributeError:
            return None

    @property
    def surface(self) -> Optional[str]:
        """
        Extract the BRepFace or ConstructionPlane to which the dimension is anchored.

        Returns:
            str: The entity token of the surface, or None if not available.
        """
        try:
            return nested_getattr(self._obj, 'surface.entityToken', None)
        except AttributeError:
            return None

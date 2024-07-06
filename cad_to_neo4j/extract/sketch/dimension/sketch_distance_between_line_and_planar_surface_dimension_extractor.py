"""
Sketch Distance Between Line and Planar Surface Dimension Extractor Module

This module provides an extractor class for extracting information from SketchDistanceBetweenLineAndPlanarSurfaceDimension objects.

Classes:
    - SketchDistanceBetweenLineAndPlanarSurfaceDimensionExtractor: Extractor for SketchDistanceBetweenLineAndPlanarSurfaceDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchDistanceBetweenLineAndPlanarSurfaceDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchDistanceBetweenLineAndPlanarSurfaceDimensionExtractor']

class SketchDistanceBetweenLineAndPlanarSurfaceDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchDistanceBetweenLineAndPlanarSurfaceDimension objects."""

    def __init__(self, obj: SketchDistanceBetweenLineAndPlanarSurfaceDimension):
        """
        Initialize the extractor with the SketchDistanceBetweenLineAndPlanarSurfaceDimension element.

        Args:
            obj (SketchDistanceBetweenLineAndPlanarSurfaceDimension): The SketchDistanceBetweenLineAndPlanarSurfaceDimension object to extract information from.
        """
        super().__init__(obj)

    @property
    def line(self) -> Optional[str]:
        """
        Extract the sketch line being constrained.

        Returns:
            str: The entity token of the sketch line, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'line.entityToken', None)
        except AttributeError:
            return None

    @property
    def planar_surface(self) -> Optional[str]:
        """
        Extract the planar surface the dimension is anchored to.

        Returns:
            str: The entity token of the planar surface, or None if not available.
        """
        try:
            return nested_getattr(self._obj, 'planarSurface.entityToken', None)
        except AttributeError:
            return None

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchDistanceBetweenLineAndPlanarSurfaceDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'line': self.line,
            'planar_surface': self.planar_surface,
        }

        return {**basic_info, **dimension_info}

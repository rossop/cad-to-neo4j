"""
Sketch Ellipse Major Radius Dimension Extractor Module

This module provides an extractor class for extracting information from SketchEllipseMajorRadiusDimension objects.

Classes:
    - SketchEllipseMajorRadiusDimensionExtractor: Extractor for SketchEllipseMajorRadiusDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchEllipseMajorRadiusDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchEllipseMajorRadiusDimensionExtractor']

class SketchEllipseMajorRadiusDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchEllipseMajorRadiusDimension objects."""

    def __init__(self, obj: SketchEllipseMajorRadiusDimension):
        """
        Initialize the extractor with the SketchEllipseMajorRadiusDimension element.

        Args:
            obj (SketchEllipseMajorRadiusDimension): The SketchEllipseMajorRadiusDimension object to extract information from.
        """
        super().__init__(obj)

    @property
    def ellipse(self) -> Optional[str]:
        """
        Extract the ellipse or elliptical arc being constrained.

        Returns:
            str: The entity token of the ellipse or elliptical arc, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'ellipse.entityToken', None)
        except AttributeError:
            return None

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchEllipseMajorRadiusDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'ellipse': self.ellipse,
        }

        return {**basic_info, **dimension_info}

"""
Sketch Ellipse Minor Radius Dimension Extractor Module

This module provides an extractor class for extracting information from SketchEllipseMinorRadiusDimension objects.

Classes:
    - SketchEllipseMinorRadiusDimensionExtractor: Extractor for SketchEllipseMinorRadiusDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchEllipseMinorRadiusDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.extraction_utils import nested_getattr

__all__ = ['SketchEllipseMinorRadiusDimensionExtractor']

class SketchEllipseMinorRadiusDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchEllipseMinorRadiusDimension objects."""

    def __init__(self, obj: SketchEllipseMinorRadiusDimension):
        """
        Initialize the extractor with the SketchEllipseMinorRadiusDimension element.

        Args:
            obj (SketchEllipseMinorRadiusDimension): The SketchEllipseMinorRadiusDimension object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchEllipseMinorRadiusDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'ellipse': self.ellipse,
        }

        return {**basic_info, **dimension_info}

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

"""
Sketch Ellipse Extractor Module

This module provides an extractor class for extracting information from SketchEllipse objects.

Classes:
    - SketchEllipseExtractor: Extractor for SketchEllipse objects.
"""

from typing import Optional, Dict, Any
from adsk.core import Vector3D, Ellipse3D
from adsk.fusion import SketchEllipse
from .sketch_entity_extractor import SketchEntityExtractor
from ...utils.extraction_utils import nested_getattr

__all__ = ['SketchEllipseExtractor']

class SketchEllipseExtractor(SketchEntityExtractor):
    """Extractor for extracting detailed information from SketchEllipse objects."""
    
    def __init__(self, obj: SketchEllipse) -> None:
        """Initialize the extractor with the SketchEllipse element."""
        super().__init__(obj)
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchEllipse element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        ellipse_info = {
            'centerPoint': self.centerSketchPoint,
            'majorAxisRadius': self.majorAxisRadius,
            'minorAxisRadius': self.minorAxisRadius,
        }
        return {**basic_info, **ellipse_info}

    @property
    def centerSketchPoint(self) -> Optional[str]:
        """Extract the center sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'centerSketchPoint.entityToken', None)
        except AttributeError:
            return None 


    @property
    def majorAxisRadius(self) -> Optional[float]:
        """Extract the major axis radius of the ellipse."""
        try:
            return nested_getattr(self._obj, "majorAxisRadius", None)
        except AttributeError:
            return None

    @property
    def minorAxisRadius(self) -> Optional[float]:
        """Extract the minor axis radius of the ellipse."""
        try:
            return nested_getattr(self._obj, "minorAxisRadius", None)
        except AttributeError:
            return None

    # @property
    # def geometry(self) -> Optional[Ellipse3D]:
    #     """Extract the transient geometry of the ellipse."""
    #     try:
    #         return nested_getattr(self._obj, "geometry", None)
    #     except AttributeError:
    #         return None

    # @property
    # def worldGeometry(self) -> Optional[Ellipse3D]:
    #     """Extract the world geometry of the ellipse."""
    #     try:
    #         return nested_getattr(self._obj, "worldGeometry", None)
    #     except AttributeError:
    #         return None

    # @property
    # def majorAxis(self) -> Optional[Vector3D]:
    #     """Extract the major axis direction of the ellipse."""
    #     try:
    #         return nested_getattr(self._obj, "majorAxis", None)
    #     except AttributeError:
    #         return None
    
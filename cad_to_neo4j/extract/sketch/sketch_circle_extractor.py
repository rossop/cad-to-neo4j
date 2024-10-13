"""
Sketch Circle Extractor Module

This module provides an extractor class for extracting information from SketchCircle objects.

Classes:
    - SketchCircleExtractor: Extractor for SketchCircle objects.
"""
from typing import Optional, Dict, Any
from adsk.fusion import SketchCircle
from .sketch_curve_extractor import SketchCurveExtractor
from ...utils.extraction_utils import nested_getattr

__all__ = ['SketchCircleExtractor']

class SketchCircleExtractor(SketchCurveExtractor):
    """Extractor for extracting detailed information from SketchCircle objects."""
    
    def __init__(self, obj: SketchCircle) -> None:
        """Initialize the extractor with the SketchCircle element."""
        super().__init__(obj)
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchCircle element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        circle_info = {
            'centerPoint': self.centerSketchPoint,
            'radius': self.radius,
        }
        return {**basic_info, **circle_info}

    @property
    def centerSketchPoint(self) -> Optional[str]:
        """Extract the center sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'centerSketchPoint.entityToken', None)
        except AttributeError:
            return None 

    @property
    def radius(self) -> Optional[float]:
        """Extract the radius of the sketch circle."""
        try:
            return nested_getattr(self._obj, "geometry.radius", None)
        except AttributeError:
            return None
"""
Sketch Arc Extractor Module

This module provides an extractor class for extracting information from SketchArc objects.

Classes:
    - SketchArcExtractor: Extractor for SketchArc objects.
"""
from typing import Optional, Dict, Any
from adsk.fusion import SketchArc
from .sketch_curve_extractor import SketchCurveExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['SketchArcExtractor']

class SketchArcExtractor(SketchCurveExtractor):
    """Extractor for extracting detailed information from SketchArc objects."""
    
    def __init__(self, obj: SketchArc) -> None:
        """Initialize the extractor with the SketchArc element."""
        super().__init__(obj)

    @property
    def centerSketchPoint(self):
        """Extract the center sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'centerSketchPoint.entityToken', None)
        except AttributeError:
            return None 

    @property
    def radius(self) -> Optional[float]:
        """Extract the radius of the sketch arc."""
        try:
            return self._obj.geometry.radius
        except AttributeError:
            return None
    
    @property
    def startSketchPoint(self):
        """Extract the starting sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'startSketchPoint.entityToken', None)
        except AttributeError:
            return None 

    @property
    def endSketchPoint(self):
        """Extract the ending sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'endSketchPoint.entityToken', None)
        except AttributeError:
            return None
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchArc element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        arc_info = {
            'centerPoint': self.centerSketchPoint,
            'radius': self.radius,
            'startPoint': self.startSketchPoint,
            'endPoint': self.endSketchPoint,
        }
        return {**basic_info, **arc_info}

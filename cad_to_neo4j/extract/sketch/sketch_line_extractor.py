"""
Sketch Line Extractor Module

This module provides an extractor class for extracting information from SketchLine objects.

Classes:
    - SketchLineExtractor: Extractor for SketchLine objects.
"""
from typing import Optional, Dict, Any
from adsk.fusion import SketchLine
from .sketch_curve_extractor import SketchCurveExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['SketchLineExtractor']

class SketchLineExtractor(SketchCurveExtractor):
    """Extractor for extracting detailed information from SketchLine objects."""
    
    def __init__(self, obj: SketchLine) -> None:
        """Initialize the extractor with the SketchLine element."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchLine element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        line_info = {
            'startPoint': self.startSketchPoint,
            'endPoint': self.endSketchPoint,
        }
        return {**basic_info, **line_info}
    
    @property
    def startSketchPoint(self) -> Optional[str]:
        """Extract the starting sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'startSketchPoint.entityToken', None)
        except AttributeError:
            return None 

    @property
    def endSketchPoint(self) -> Optional[str]:
        """Extract the ending sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'endSketchPoint.entityToken', None)
        except AttributeError:
            return None
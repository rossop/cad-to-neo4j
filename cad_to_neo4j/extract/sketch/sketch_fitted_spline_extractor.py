"""
Sketch Fitted Spline Extractor Module

This module provides an extractor class for extracting information from SketchFittedSpline objects.

Classes:
    - SketchFittedSplineExtractor: Extractor for SketchFittedSpline objects.
"""

from typing import Optional, Dict, Any, List
from adsk.core import NurbsCurve3D
from adsk.fusion import SketchFittedSpline
from .sketch_entity_extractor import SketchEntityExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['SketchFittedSplineExtractor']

class SketchFittedSplineExtractor(SketchEntityExtractor):
    """Extractor for extracting detailed information from SketchFittedSpline objects."""
    
    def __init__(self, obj: SketchFittedSpline) -> None:
        """Initialize the extractor with the SketchFittedSpline element."""
        super().__init__(obj)
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchFittedSpline element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        spline_info = {
            'startPoint': self.startSketchPoint,
            'endPoint': self.endSketchPoint,
            'fitPoints': self.fitPoints,
            'isClosed': self.isClosed,
        }
        return {**basic_info, **spline_info}

    @property
    def startSketchPoint(self) -> Optional[str]:
        """Extract the start sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'startSketchPoint.entityToken', None)
        except AttributeError:
            return None

    @property
    def endSketchPoint(self) -> Optional[str]:
        """Extract the end sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'endSketchPoint.entityToken', None)
        except AttributeError:
            return None

    @property
    def fitPoints(self) -> Optional[List[str]]:
        """Extract the fit points entity tokens."""
        try:
            fit_points = getattr(self._obj, 'fitPoints', [])
            return [nested_getattr(point, 'entityToken', None) for point in fit_points]
        except AttributeError:
            return None

    @property
    def isClosed(self) -> Optional[bool]:
        """Extract the closed status of the spline."""
        try:
            return getattr(self._obj, 'isClosed', None)
        except AttributeError:
            return None
    
    # @property
    # def geometry(self) -> Optional[NurbsCurve3D]:
    #     """Extract the transient geometry of the spline."""
    #     try:
    #         return nested_getattr(self._obj, "geometry", None)
    #     except AttributeError:
    #         return None

    # @property
    # def worldGeometry(self) -> Optional[NurbsCurve3D]:
    #     """Extract the world geometry of the spline."""
    #     try:
    #         return nested_getattr(self._obj, "worldGeometry", None)
    #     except AttributeError:
    #         return None

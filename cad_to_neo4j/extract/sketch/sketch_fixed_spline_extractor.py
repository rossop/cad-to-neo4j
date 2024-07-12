"""
Sketch Fixed Spline Extractor Module

This module provides an extractor class for extracting information from SketchFixedSpline objects.

Classes:
    - SketchFixedSplineExtractor: Extractor for SketchFixedSpline objects.
"""

from typing import Optional, Dict, Any
from adsk.core import NurbsCurve3D, CurveEvaluator3D
from adsk.fusion import SketchFixedSpline
from .sketch_entity_extractor import SketchEntityExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['SketchFixedSplineExtractor']

class SketchFixedSplineExtractor(SketchEntityExtractor):
    """Extractor for extracting detailed information from SketchFixedSpline objects."""
    
    def __init__(self, obj: SketchFixedSpline) -> None:
        """Initialize the extractor with the SketchFixedSpline element."""
        super().__init__(obj)
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchFixedSpline element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        fixed_spline_info = {
            'startPoint': self.startSketchPoint,
            'endPoint': self.endSketchPoint,
            'geometry': self.geometry,
            'worldGeometry': self.worldGeometry,
            'evaluator': self.evaluator,
        }
        return {**basic_info, **fixed_spline_info}

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
    def geometry(self) -> Optional[NurbsCurve3D]:
        """Extract the transient geometry of the fixed spline."""
        try:
            return nested_getattr(self._obj, "geometry", None)
        except AttributeError:
            return None

    @property
    def worldGeometry(self) -> Optional[NurbsCurve3D]:
        """Extract the world geometry of the fixed spline."""
        try:
            return nested_getattr(self._obj, "worldGeometry", None)
        except AttributeError:
            return None

    @property
    def evaluator(self) -> Optional[CurveEvaluator3D]:
        """Extract the evaluator for the fixed spline."""
        try:
            return nested_getattr(self._obj, "evaluator", None)
        except AttributeError:
            return None
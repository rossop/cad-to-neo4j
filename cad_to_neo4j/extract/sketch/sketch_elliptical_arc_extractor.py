"""
Sketch Elliptical Arc Extractor Module

This module provides an extractor class for extracting information from SketchEllipticalArc objects.

Classes:
    - SketchEllipticalArcExtractor: Extractor for SketchEllipticalArc objects.
"""

from typing import Optional, Dict, Any
from adsk.core import Vector3D, EllipticalArc3D
from adsk.fusion import SketchEllipticalArc
from .sketch_entity_extractor import SketchEntityExtractor
from ...utils.extraction_utils import nested_getattr

__all__ = ['SketchEllipticalArcExtractor']

class SketchEllipticalArcExtractor(SketchEntityExtractor):
    """Extractor for extracting detailed information from SketchEllipticalArc objects."""
    
    def __init__(self, obj: SketchEllipticalArc) -> None:
        """Initialize the extractor with the SketchEllipticalArc element."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchEllipticalArc element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        elliptical_arc_info = {
            'centerPoint': self.centerSketchPoint,
            'startPoint': self.startSketchPoint,
            'endPoint': self.endSketchPoint,
            'majorAxisRadius': self.majorAxisRadius,
            'minorAxisRadius': self.minorAxisRadius,
        }
        return {**basic_info, **elliptical_arc_info}

    @property
    def centerSketchPoint(self) -> Optional[str]:
        """Extract the center sketch point entity token."""
        try:
            return nested_getattr(self._obj, 'centerSketchPoint.entityToken', None)
        except AttributeError:
            return None 

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
    def majorAxisRadius(self) -> Optional[float]:
        """Extract the major axis radius of the elliptical arc."""
        try:
            return nested_getattr(self._obj, "majorAxisRadius", None)
        except AttributeError:
            return None

    @property
    def minorAxisRadius(self) -> Optional[float]:
        """Extract the minor axis radius of the elliptical arc."""
        try:
            return nested_getattr(self._obj, "minorAxisRadius", None)
        except AttributeError:
            return None

    # @property
    # def majorAxis(self) -> Optional[Vector3D]:
    #     """Extract the major axis direction of the elliptical arc."""
    #     try:
    #         return nested_getattr(self._obj, "majorAxis", None)
    #     except AttributeError:
    #         return None

    # @property
    # def geometry(self) -> Optional[EllipticalArc3D]:
    #     """Extract the transient geometry of the elliptical arc."""
    #     try:
    #         return nested_getattr(self._obj, "geometry", None)
    #     except AttributeError:
    #         return None

    # @property
    # def worldGeometry(self) -> Optional[EllipticalArc3D]:
    #     """Extract the world geometry of the elliptical arc."""
    #     try:
    #         return nested_getattr(self._obj, "worldGeometry", None)
    #     except AttributeError:
    #         return None
    
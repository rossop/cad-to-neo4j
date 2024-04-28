"""
Sketch Extractor Module

This module provides an extractor class for extracting information from Sketch objects,
including SketchPoints, SketchCurves, and SketchDimensions.

Classes:
    - SketchExtractor: Extractor for Sketch objects.
    - SketchPointExtractor: Extractor for SketchPoint objects.
    - SketchCurveExtractor: Extractor for SketchCurve objects.
    - SketchDimensionExtractor: Extractor for SketchDimension objects.
"""
from typing import Optional, Dict, List, Any
from adsk.fusion import Sketch
from ..base_extractor import BaseExtractor
from ...utils.general_utils import nested_getattr
from .sketch_element_extractor import SketchElementExtractor
import adsk.core, traceback

__all__ = ['SketchExtractor']
class SketchExtractor(SketchElementExtractor):
    """Extractor for extracting detailed information from Sketch objects."""

    def __init__(self, element: Sketch):
        """Initialize the extractor with the Sketch element."""
        super().__init__(element)

    def extract_info(self) -> dict:
        """Extract all information from the Sketch element.
        
        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_info = {
            'timeline_index': self.timeline_index,
            'reference_plane_entity_token': self.reference_plane_entity_token
        }
        return {**basic_info, **sketch_info}
    
    @property
    def timeline_index(self) -> Optional[int]:
        """Extracts the timeline index of the Sketch object.
        
        Returns:
            int: The timeline index of the Sketch object, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'timelineObject.index', None)
        except AttributeError:
            return None
        
    @property
    def reference_plane_entity_token(self) -> Optional[str]:
        """
        Extracts the entity token of the face or plane the sketch is built on.

        This method checks for the referencePlane attribute of the Sketch object,
        which provides information about the plane or face the sketch is created on.
        If the attribute exists, it returns the entity token of the reference plane.

        Returns:
            Optional[str]: The entity token of the reference plane, or None if not available.
        """
        if hasattr(self._obj, 'referencePlane'):
            return nested_getattr(self._obj, 'referencePlane.entityToken', None)
        return None
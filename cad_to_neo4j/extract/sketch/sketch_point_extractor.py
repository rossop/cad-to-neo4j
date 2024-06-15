"""
Sketch Point Extractor Module

This module provides an extractor class for extracting information from SketchPoint objects.

Classes:
    - SketchPointExtractor: Extractor for SketchPoint objects.
"""
from typing import Optional, Dict, List, Any
from adsk.fusion import SketchPoint
from .sketch_element_extractor import SketchElementExtractor
from ..base_extractor import BaseExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['SketchPointExtractor']

class SketchPointExtractor(SketchElementExtractor):
    """Extractor for extracting detailed information from Sketch Point objects."""

    def __init__(self, obj: SketchPoint) -> None:
        """Initialize the extractor with the SketchPoint element."""
        super().__init__(obj)

    @property
    def coordinates(self) -> Optional[List[float]]:
        """Extract the coordinates of the sketch point."""
        try:
            return nested_getattr(self._obj, "geometry.asArray", None)
        except AttributeError:
            return None

    @property
    def connectedEntities(self) -> Optional[List[str]]:
        """Extract the entities connected to the sketch point."""
        try:
            connectedEntities = getattr(self._obj, 'connectedEntities', [])
            if connectedEntities is None:
                connectedEntities = []
            id_tokens = []
            for e in connectedEntities:
                token = getattr(e,'entityToken', None) 
                if token is not None:
                    id_tokens.append(token)
            return id_tokens
        except AttributeError:
            return None
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchPoint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        point_info = {
            'connectedEntities': self.connectedEntities,
        }
        return {**basic_info, **point_info}
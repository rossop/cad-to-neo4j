"""
Sketch Point Extractor Module

This module provides an extractor class for extracting information from SketchPoint objects.

Classes:
    - SketchPointExtractor: Extractor for SketchPoint objects.
"""
from typing import Optional, Dict, List, Any

import adsk.fusion

from .sketch_entity_extractor import SketchEntityExtractor
from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error

__all__ = ['SketchPointExtractor']


class SketchPointExtractor(SketchEntityExtractor):
    """
    Extractor for extracting detailed information from Sketch Point objects.
    """

    def __init__(self, obj: adsk.fusion.SketchPoint) -> None:
        """Initialize the extractor with the SketchPoint element."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the SketchPoint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        point_info = {
            'connectedEntities': self.connected_entities,
        }
        return {**basic_info, **point_info}

    @property
    @helper_extraction_error
    def coordinates(self) -> Optional[List[float]]:
        """Extract the coordinates of the sketch point."""
        return nested_getattr(self._obj, "geometry.asArray", None)

    @property
    @helper_extraction_error
    def connected_entities(self) -> Optional[List[str]]:
        """Extract the entities connected to the sketch point."""
        connected_entities = getattr(self._obj, 'connectedEntities', [])
        if connected_entities is None:
            connected_entities = []
        entity_tokens = []
        for e in connected_entities:
            token = getattr(e, 'entityToken', None)
            if token is not None:
                entity_tokens.append(token)
        return entity_tokens

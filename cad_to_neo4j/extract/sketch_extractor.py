"""
Sketch Extractor Module

This module provides an extractor class for extracting information from Sketch objects.

Classes:
    - SketchExtractor: Extractor for Sketch objects.
"""
from typing import Optional
from adsk.fusion import Sketch
from .base_extractor import BaseExtractor

__all__ = ['SketchExtractor']

class SketchExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Sketch objects."""

    def __init__(self, element: Sketch):
        """Initialize the extractor with the Sketch element."""
        super().__init__(element)

    @property
    def timeline_index(self) -> Optional[int]:
        """Extracts the timeline index of the Sketch object.
        
        Returns:
            int: The timeline index of the Sketch object, or None if not available.
        """
        try:
            return self._obj.timelineObject.index
        except AttributeError:
            return None
    
    def extract_info(self) -> dict:
        """Extract all information from the Sketch element.
        
        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_info = {
            'timeline_index': self.timeline_index
        }
        return {**basic_info, **sketch_info}

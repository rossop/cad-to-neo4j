"""
Feature Extractor Module

This module provides an extractor class for extracting information from Feature objects.

Classes:
    - FeatureExtractor: Extractor for Feature objects.
"""
from typing import Optional
from adsk.fusion import Feature
from ..base_extractor import BaseExtractor

__all__ = ['FeatureExtractor']

class FeatureExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Feature objects."""

    def __init__(self, element: Feature):
        """Initialize the extractor with the Feature element."""
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
        """Extract all information from the Feature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        feature_info = {
            'timeline_index': self.timeline_index
        }
        return {**basic_info, **feature_info}

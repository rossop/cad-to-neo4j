"""
Feature Extractor Module

This module provides an extractor class for extracting information from Feature objects.

Classes:
    - FeatureExtractor: Extractor for Feature objects.
"""
from typing import Optional, List, Dict
from adsk.fusion import Feature
from ..base_extractor import BaseExtractor
import traceback
from ...utils.general_utils import nested_getattr

__all__ = ['FeatureExtractor']

class FeatureExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Feature objects."""

    def __init__(self, element: Feature):
        """Initialize the extractor with the Feature element."""
        super().__init__(element)
        
    @property
    def faces(self) -> Optional[List[str]]:
        """Extracts the IDs of side faces created by the feature."""
        try:
            return self.extract_ids('faces', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting side faces: {e}\n{traceback.format_exc()}')
            return None
        
    def roll_timeline_to_before_feature(self):
        """Roll the timeline to immediately before this feature."""
        try:
            self._obj.timelineObject.rollTo(True)
        except Exception as e:
            self.logger.error(f'Failed to roll timeline before feature: {e}')

    def roll_timeline_to_after_feature(self):
        """Roll the timeline to immediately after this feature."""
        try:
            self._obj.timelineObject.rollTo(False)
        except Exception as e:
            self.logger.error(f'Failed to roll timeline after feature: {e}')

    def extract_ids_with_timeline(self, attribute: str, id_attribute: str) -> Optional[List[str]]:
        """Extract IDs from an attribute with timeline rollback."""
        self.roll_timeline_to_before_feature()
        ids = self.extract_ids(attribute, id_attribute)
        self.roll_timeline_to_after_feature()
        return ids
    
    def extract_info(self) -> dict:
        """Extract all information from the Feature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        feature_info = {
            'faces': self.faces,
            
        }
        return {**basic_info, **feature_info}

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

    def __init__(self, obj: Feature):
        """Initialize the extractor with the Feature element."""
        super().__init__(obj)
        
    @property
    def faces(self) -> Optional[List[str]]:
        """Extracts the IDs of side faces created by the feature."""
        try:
            return self.extract_ids('faces', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting side faces: {e}\n{traceback.format_exc()}')
            return None

    @property
    def is_suppressed(self) -> Optional[bool]:
        """Extracts whether the feature is suppressed."""
        try:
            return self._obj.isSuppressed
        except AttributeError as e:
            self.logger.error(f'Error extracting isSuppressed: {e}\n{traceback.format_exc()}')
            return None
    
    @property
    def isParametric(self) -> Optional[bool]:
        """Extracts whether the feature is parametric."""
        try:
            return self._obj.isParametric
        except AttributeError as e:
            self.logger.error(f'Error extracting isParametric: {e}\n{traceback.format_exc()}')
            return None
    
    @property
    def parentComponent(self) -> Optional[str]:
        """Extracts the ID of the parent component."""
        try:
            return self._obj.parentComponent.entityToken
        except AttributeError as e:
            self.logger.error(f'Error extracting parentComponent: {e}\n{traceback.format_exc()}')
            return None
    
    @property
    def linked_features(self) -> Optional[List[str]]:
        """Extracts the IDs of linked features."""
        try:
            return self.extract_ids('linkedFeatures', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting linkedFeatures: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def bodies(self) -> Optional[List[str]]:
        """Extracts the IDs of bodies modified or created by the feature."""
        try:
            return self.extract_ids('bodies', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting bodies: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def base_feature(self) -> Optional[str]:
        """Extracts the ID of the associated base feature, if any."""
        try:
            return self._obj.baseFeature.entityToken if self._obj.baseFeature else None
        except AttributeError as e:
            self.logger.error(f'Error extracting baseFeature: {e}\n{traceback.format_exc()}')
            return None

    @property
    def healthState(self) -> Optional[str]:
        """Extracts the current health state of the feature."""
        try:
            return self._obj.healthState
        except AttributeError as e:
            self.logger.error(f'Error extracting healthState: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def errorOrWarningMessage(self) -> Optional[str]:
        """Extracts the error or warning message if the feature has health issues."""
        try:
            return self._obj.errorOrWarningMessage
        except AttributeError as e:
            self.logger.error(f'Error extracting errorOrWarningMessage: {e}\n{traceback.format_exc()}')
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
            'is_suppressed': self.is_suppressed,
            'isParametric': self.isParametric,
            'parentComponent': self.parentComponent,
            'linked_features': self.linked_features,
            'bodies': self.bodies,
            'base_feature': self.base_feature,
            'healthState': self.healthState,
            'errorOrWarningMessage': self.errorOrWarningMessage,
        }
        return {**basic_info, **feature_info}


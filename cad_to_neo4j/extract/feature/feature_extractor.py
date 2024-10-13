"""
Feature Extractor Module

This module provides an extractor class for extracting information from
Feature objects.

Classes:
    - FeatureExtractor: Extractor for Feature objects.
"""
from typing import Any, Optional, List, Dict
import adsk.fusion

from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import helper_extraction_error

__all__ = ['FeatureExtractor']


class FeatureExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Feature objects."""

    def __init__(self, obj: adsk.fusion.Feature):
        """Initialize the extractor with the Feature element."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the Feature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        feature_info = {
            'faces': self.faces,
            'isSuppressed': self.is_suppressed,
            'isParametric': self.is_parametric,
            'parentComponent': self.parent_component,
            'linkedFeatures': self.linked_features,
            'bodies': self.bodies,
            'baseFeature': self.base_feature,
            'healthState': self.health_state,
            'errorOrWarningMessage': self.error_or_warning_message,
        }
        return {**basic_info, **feature_info}

    @property
    @helper_extraction_error
    def faces(self) -> Optional[List[str]]:
        """Extracts the IDs of side faces created by the feature."""
        return self.extract_collection_tokens('faces', 'entityToken')

    @property
    @helper_extraction_error
    def is_suppressed(self) -> Optional[bool]:
        """Extracts whether the feature is suppressed."""
        return self._obj.isSuppressed

    @property
    @helper_extraction_error
    def is_parametric(self) -> Optional[bool]:
        """Extracts whether the feature is parametric."""
        return self._obj.isParametric

    @property
    @helper_extraction_error
    def parent_component(self) -> Optional[str]:
        """Extracts the ID of the parent component."""
        return self._obj.parentComponent.entityToken

    @property
    @helper_extraction_error
    def linked_features(self) -> Optional[List[str]]:
        """Extracts the IDs of linked features."""
        return self.extract_collection_tokens('linkedFeatures', 'entityToken')

    @property
    @helper_extraction_error
    def bodies(self) -> Optional[List[str]]:
        """Extracts the IDs of bodies modified or created by the feature."""
        return self.extract_collection_tokens('bodies', 'entityToken')

    @property
    @helper_extraction_error
    def base_feature(self) -> Optional[str]:
        """Extracts the ID of the associated base feature, if any."""
        return self._obj.baseFeature.entityToken \
            if self._obj.baseFeature else None

    @property
    @helper_extraction_error
    def health_state(self) -> Optional[str]:
        """Extracts the current health state of the feature."""
        return self._obj.healthState

    @property
    @helper_extraction_error
    def error_or_warning_message(self) -> Optional[str]:
        """
        Extracts the error or warning message if the feature has health issues.
        """
        return self._obj.errorOrWarningMessage

    def roll_timeline_to_before_feature(self):
        """Roll the timeline to immediately before this feature."""
        try:
            self._obj.timelineObject.rollTo(True)
        except Exception as e:
            exception_msg: str = f'Failed to roll timeline before feature: {e}'
            self.logger.error(exception_msg)

    def roll_timeline_to_after_feature(self):
        """Roll the timeline to immediately after this feature."""
        try:
            self._obj.timelineObject.rollTo(False)
        except Exception as e:
            exception_msg: str = f'Failed to roll timeline after feature: {e}'
            self.logger.error(exception_msg)

    @helper_extraction_error
    def extract_ids_with_timeline(
            self, attribute: str, id_attribute: str) -> Optional[List[str]]:
        """Extract IDs from an attribute with timeline rollback."""
        self.roll_timeline_to_before_feature()
        ids = self.extract_collection_tokens(attribute, id_attribute)
        self.roll_timeline_to_after_feature()
        return ids

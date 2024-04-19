"""
Extrude Feature Extractor Module

This module provides an extractor class for extracting information from ExtrudeFeature objects.

Classes:
    - ExtrudeFeatureExtractor: Extractor for ExtrudeFeature objects.
"""
from adsk.fusion import ExtrudeFeature
import adsk.core
from .feature_extractor import FeatureExtractor

__all__ = ['ExtrudeFeatureExtractor']

class ExtrudeFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from ExtrudeFeature objects."""

    def __init__(self, element: ExtrudeFeature):
        """Initialize the extractor with the ExtrudeFeature element."""
        super().__init__(element)

    @property
    def profile_tokens(self):
        """Extracts the tokens of profiles used by the ExtrudeFeature.

        Returns:
            list: A list of profile tokens used by the ExtrudeFeature.
        """
        try:
            profiles = self._obj.profile
            if isinstance(profiles, adsk.core.ObjectCollection):
                return [profile.entityToken for profile in profiles]
            return [profiles.entityToken]
        except AttributeError:
            return []

    def extract_info(self) -> dict:
        """Extract all information from the ExtrudeFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        extrude_info = {
            'profile_tokens': self.profile_tokens
        }
        return {**feature_info, **extrude_info}

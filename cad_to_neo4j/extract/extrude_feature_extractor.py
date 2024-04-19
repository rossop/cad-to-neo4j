"""
Extrude Feature Extractor Module

This module provides an extractor class for extracting information from ExtrudeFeature objects.

Classes:
    - ExtrudeFeatureExtractor: Extractor for ExtrudeFeature objects.
"""
from adsk.fusion import ExtrudeFeature
from .feature_extractor import FeatureExtractor

__all__ = ['ExtrudeFeatureExtractor']

class ExtrudeFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from ExtrudeFeature objects."""

    def __init__(self, element: ExtrudeFeature):
        """Initialize the extractor with the ExtrudeFeature element."""
        super().__init__(element)

    @property
    def profile(self):
        """Extracts the profiles used by the ExtrudeFeature.

        Returns:
            list: A list of profiles used by the ExtrudeFeature.
        """
        try:
            profiles = self._obj.profile
            if isinstance(profiles, adsk.core.ObjectCollection):
                return [profile for profile in profiles]
            return [profiles]
        except AttributeError:
            return []

    def extract_info(self) -> dict:
        """Extract all information from the ExtrudeFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        extrude_info = {}
        return {**feature_info, **extrude_info}

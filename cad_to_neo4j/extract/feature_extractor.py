"""
Feature Extractor Module

This module provides an extractor class for extracting information from Feature objects.

Classes:
    - FeatureExtractor: Extractor for Feature objects.
"""

from adsk.fusion import Feature
from .base_extractor import BaseExtractor

__all__ = ['FeatureExtractor']

class FeatureExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Feature objects."""

    def __init__(self, element: Feature):
        """Initialize the extractor with the Feature element."""
        super().__init__(element)

    def extract_info(self) -> dict:
        """Extract all information from the Feature element."""
        info = super().extract_info()
        # Add more feature-specific extraction logic here
        return info

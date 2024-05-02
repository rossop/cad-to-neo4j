"""
Feature Extractor Module

This module provides extractors for extracting information from feature objects, including extrude features.

Classes:
    - FeatureExtractor: Extractor for feature objects.
    - ExtrudeFeatureExtractor: Extractor for extrude feature objects.
"""

from .feature_extractor import FeatureExtractor
from .extrude_feature_extractor import ExtrudeFeatureExtractor

__all__ = ['FeatureExtractor', 'ExtrudeFeatureExtractor']

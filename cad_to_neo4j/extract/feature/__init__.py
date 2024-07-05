"""
Feature Extractor Module

This module provides extractors for extracting information from feature objects, including extrude features.

Classes:
    - FeatureExtractor: Extractor for feature objects.
    - ExtrudeFeatureExtractor: Extractor for extrude feature objects.
    - RevolveFeatureExtractor: Extractor for revolve feature objects.
"""

from .feature_extractor import FeatureExtractor
from .extrude_feature_extractor import ExtrudeFeatureExtractor
from .revolve_feature_extractor import RevolveFeatureExtractor
from .hole_feature_extractor import HoleFeatureExtractor
from .fillet_feature_extractor import FilletFeatureExtractor
from .box_feature_extractor import BoxFeatureExtractor

__all__ = [
    'FeatureExtractor', 
    'ExtrudeFeatureExtractor', 
    'RevolveFeatureExtractor',
    'HoleFeatureExtractor',
    'FilletFeatureExtractor',
    'BoxFeatureExtractor',
    ]

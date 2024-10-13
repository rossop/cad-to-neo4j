"""
Feature Extractor Module

This module provides extractors for extracting information from feature
objects, including extrude features.

Classes:
    - FeatureExtractor: Extractor for feature objects.
    - ExtrudeFeatureExtractor: Extractor for extrude feature objects.
    - RevolveFeatureExtractor: Extractor for revolve feature objects.
    - HoleFeatureExtractor: Extractor for HoleFeature objects
    - FilletFeatureExtractor: Extractor for FilletFeature objects
    - ChamferFeatureExtractor: Extractor for ChamferFeature objects
    - BoxFeatureExtractor: Extractor for BoxFeature objects
    - ConstantRadiusFilletEdgeSetExtractor: Extractor for
        ConstantRadiusFilletEdgeSet objects
    - VariableRadiusFilletEdgeSetExtractor: Extractor for
        VariableRadiusFilletEdgeSet objects
    - ChordLengthFilletEdgeSetExtractor: Extractor for ChordLengthFilletEdgeSet
        objects
    - EqualDistanceEdgeSetExtractor: Extractor for EqualDistanceEdgeSet objects
    - TwoDistancesEdgeSetExtractor: Extractor for TwoDistancesEdgeSet objects
    - DistanceAndAngleEdgeSetExtractor: Extractor for DistanceAndAngleEdgeSet
        objects
    - RectangularPatternFeatureExtractor: Extractor for
        RectangularPatternFeature objects
"""

from .feature_extractor import FeatureExtractor
from .extrude_feature_extractor import ExtrudeFeatureExtractor
from .revolve_feature_extractor import RevolveFeatureExtractor
from .hole_feature_extractor import HoleFeatureExtractor
from .fillet_feature_extractor import FilletFeatureExtractor
from .fillet_edge_set import (
            ConstantRadiusFilletEdgeSetExtractor,
            VariableRadiusFilletEdgeSetExtractor,
            ChordLengthFilletEdgeSetExtractor
            )
from .chamfer_feature_extractor import ChamferFeatureExtractor
from .chamfer_edge_set import (
            EqualDistanceEdgeSetExtractor,
            TwoDistancesEdgeSetExtractor,
            DistanceAndAngleEdgeSetExtractor,
            )
from .box_feature_extractor import BoxFeatureExtractor
from .rectangular_pattern_feature_extractor import (
    RectangularPatternFeatureExtractor,
)
from .path_pattern_feature_extractor import (
    PathPatternFeatureExtractor
)
from .circular_pattern_feature_extractor import (
    CircularPatternFeatureExtractor
)

__all__ = [
    'FeatureExtractor',
    'ExtrudeFeatureExtractor',
    'RevolveFeatureExtractor',
    'HoleFeatureExtractor',
    'FilletFeatureExtractor',
    'ChamferFeatureExtractor',
    'BoxFeatureExtractor',
    'ConstantRadiusFilletEdgeSetExtractor',
    'VariableRadiusFilletEdgeSetExtractor',
    'ChordLengthFilletEdgeSetExtractor',
    'EqualDistanceEdgeSetExtractor',
    'TwoDistancesEdgeSetExtractor',
    'DistanceAndAngleEdgeSetExtractor',
    'RectangularPatternFeatureExtractor',
    'PathPatternFeatureExtractor',
    'CircularPatternFeatureExtractor',
    ]

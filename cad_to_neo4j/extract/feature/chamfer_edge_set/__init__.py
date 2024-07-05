"""
Chamfer Edge Set Extractor Module

This module provides extractor classes for extracting information from different types of ChamferEdgeSet objects
in Autodesk Fusion 360. Each edge set type is handled by a specific extractor class that inherits from a common
base edge set extractor.

Classes:
    - BaseEdgeSetExtractor: Base extractor for ChamferEdgeSet objects.
    - EqualDistanceEdgeSetExtractor: Extractor for EqualDistanceChamferEdgeSet objects.
    - TwoDistancesEdgeSetExtractor: Extractor for TwoDistancesChamferEdgeSet objects.
    - DistanceAndAngleEdgeSetExtractor: Extractor for DistanceAndAngleChamferEdgeSet objects.
"""

from .equal_distance_edge_set_extractor import EqualDistanceEdgeSetExtractor
from .two_distances_edge_set_extractor import TwoDistancesEdgeSetExtractor
from .distance_and_angle_edge_set_extractor import DistanceAndAngleEdgeSetExtractor

__all__ = [
    'EqualDistanceEdgeSetExtractor',
    'TwoDistancesEdgeSetExtractor',
    'DistanceAndAngleEdgeSetExtractor',
]

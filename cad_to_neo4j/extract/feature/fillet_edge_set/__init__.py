"""
Fillet Edge Set Extractors Submodule

This submodule provides extractor classes for extracting information from different types of FilletEdgeSet objects.

Modules:
    - base_edge_set_extractor: Base extractor class for fillet edge sets.
    - constant_radius_fillet_edge_set_extractor: Extractor for ConstantRadiusFilletEdgeSet objects.
    - variable_radius_fillet_edge_set_extractor: Extractor for VariableRadiusFilletEdgeSet objects.
    - chord_length_fillet_edge_set_extractor: Extractor for ChordLengthFilletEdgeSet objects.

Classes:
    - BaseEdgeSetExtractor
    - ConstantRadiusFilletEdgeSetExtractor
    - VariableRadiusFilletEdgeSetExtractor
    - ChordLengthFilletEdgeSetExtractor
"""

from .constant_radius_fillet_edge_set_extractor import ConstantRadiusFilletEdgeSetExtractor
from .variable_radius_fillet_edge_set_extractor import VariableRadiusFilletEdgeSetExtractor
from .chord_length_fillet_edge_set_extractor import ChordLengthFilletEdgeSetExtractor

__all__ = [
    'ConstantRadiusFilletEdgeSetExtractor',
    'VariableRadiusFilletEdgeSetExtractor',
    'ChordLengthFilletEdgeSetExtractor'
]

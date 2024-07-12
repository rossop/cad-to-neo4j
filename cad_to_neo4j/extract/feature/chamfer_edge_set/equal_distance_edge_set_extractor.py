"""
Equal Distance Edge Set Extractor Module

This module provides an extractor class for extracting information from EqualDistanceChamferEdgeSet objects.

Classes:
    - EqualDistanceEdgeSetExtractor: Extractor for EqualDistanceChamferEdgeSet objects.
"""

from typing import Optional
import adsk.fusion
import traceback
from .base_edge_set_extractor import BaseEdgeSetExtractor

__all__ = ['EqualDistanceEdgeSetExtractor']

class EqualDistanceEdgeSetExtractor(BaseEdgeSetExtractor):
    """Extractor for extracting detailed information from EqualDistanceChamferEdgeSet objects."""

    def __init__(self, obj: adsk.fusion.EqualDistanceChamferEdgeSet):
        """Initialize the extractor with the EqualDistanceChamferEdgeSet element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the EqualDistanceChamferEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        edge_set_info = super().extract_info()
        chamfer_info = {
            'distance': self.distance,
        }
        return {**edge_set_info, **chamfer_info}

    @property
    def distance(self) -> Optional[float]:
        """Extracts the distance of the chamfer."""
        try:
            return self._obj.distance.value
        except AttributeError as e:
            self.logger.error(f'Error extracting distance: {e}\n{traceback.format_exc()}')
            return None

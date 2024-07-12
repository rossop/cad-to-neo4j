"""
Two Distances Edge Set Extractor Module

This module provides an extractor class for extracting information from TwoDistancesChamferEdgeSet objects.

Classes:
    - TwoDistancesEdgeSetExtractor: Extractor for TwoDistancesChamferEdgeSet objects.
"""

from typing import Optional
from adsk.fusion import TwoDistancesChamferEdgeSet
import traceback
from .base_edge_set_extractor import BaseEdgeSetExtractor

__all__ = ['TwoDistancesEdgeSetExtractor']

class TwoDistancesEdgeSetExtractor(BaseEdgeSetExtractor):
    """Extractor for extracting detailed information from TwoDistancesChamferEdgeSet objects."""

    def __init__(self, obj: TwoDistancesChamferEdgeSet):
        """Initialize the extractor with the TwoDistancesChamferEdgeSet element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the TwoDistancesChamferEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        edge_set_info = super().extract_info()
        chamfer_info = {
            'distanceOne': self.distanceOne,
            'distanceTwo': self.distanceTwo,
        }
        return {**edge_set_info, **chamfer_info}

    @property
    def distanceOne(self) -> Optional[float]:
        """Extracts the first distance of the chamfer."""
        try:
            return self._obj.distanceOne.value
        except AttributeError as e:
            self.logger.error(f'Error extracting distance one: {e}\n{traceback.format_exc()}')
            return None

    @property
    def distanceTwo(self) -> Optional[float]:
        """Extracts the second distance of the chamfer."""
        try:
            return self._obj.distanceTwo.value
        except AttributeError as e:
            self.logger.error(f'Error extracting distance two: {e}\n{traceback.format_exc()}')
            return None

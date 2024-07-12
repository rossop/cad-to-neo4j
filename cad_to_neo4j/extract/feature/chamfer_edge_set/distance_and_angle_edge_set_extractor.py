"""
Distance and Angle Edge Set Extractor Module

This module provides an extractor class for extracting information from DistanceAndAngleChamferEdgeSet objects.

Classes:
    - DistanceAndAngleEdgeSetExtractor: Extractor for DistanceAndAngleChamferEdgeSet objects.
"""

from typing import Optional
import adsk.fusion
import traceback
from .base_edge_set_extractor import BaseEdgeSetExtractor

__all__ = ['DistanceAndAngleEdgeSetExtractor']

class DistanceAndAngleEdgeSetExtractor(BaseEdgeSetExtractor):
    """Extractor for extracting detailed information from DistanceAndAngleChamferEdgeSet objects."""

    def __init__(self, obj: adsk.fusion.DistanceAndAngleChamferEdgeSet):
        """Initialize the extractor with the DistanceAndAngleChamferEdgeSet element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the DistanceAndAngleChamferEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        edge_set_info = super().extract_info()
        chamfer_info = {
            'distance': self.distance,
            'angle': self.angle,
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

    @property
    def angle(self) -> Optional[float]:
        """Extracts the angle of the chamfer."""
        try:
            return self._obj.angle.value
        except AttributeError as e:
            self.logger.error(f'Error extracting angle: {e}\n{traceback.format_exc()}')
            return None

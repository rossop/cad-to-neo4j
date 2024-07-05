"""
Variable Radius Fillet Edge Set Extractor Module

This module provides an extractor class for extracting information from VariableRadiusFilletEdgeSet objects.

Classes:
    - VariableRadiusFilletEdgeSetExtractor: Extractor for VariableRadiusFilletEdgeSet objects.
"""
from typing import Optional, List, Dict
import adsk.fusion
import traceback
from .base_edge_set_extractor import BaseEdgeSetExtractor

__all__ = ['VariableRadiusFilletEdgeSetExtractor']

class VariableRadiusFilletEdgeSetExtractor(BaseEdgeSetExtractor):
    """Extractor for extracting detailed information from VariableRadiusFilletEdgeSet objects."""

    def __init__(self, element: adsk.fusion.VariableRadiusFilletEdgeSet):
        """Initialize the extractor with the VariableRadiusFilletEdgeSet element."""
        super().__init__(element)

    @property
    def start_radius(self) -> Optional[str]:
        """Extracts the start radius of the fillet edge set."""
        try:
            return getattr(self._obj, 'startRadius', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting start radius: {e}\n{traceback.format_exc()}')
            return None

    @property
    def end_radius(self) -> Optional[str]:
        """Extracts the end radius of the fillet edge set."""
        try:
            return getattr(self._obj, 'endRadius', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting end radius: {e}\n{traceback.format_exc()}')
            return None

    @property
    def mid_radii(self) -> Optional[List[str]]:
        """Extracts the mid radii of the fillet edge set."""
        try:
            return [radius for radius in getattr(self._obj, 'midRadii', [])]
        except AttributeError as e:
            self.logger.error(f'Error extracting mid radii: {e}\n{traceback.format_exc()}')
            return None

    @property
    def mid_positions(self) -> Optional[List[str]]:
        """Extracts the mid positions of the fillet edge set."""
        try:
            return [position for position in getattr(self._obj, 'midPositions', [])]
        except AttributeError as e:
            self.logger.error(f'Error extracting mid positions: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> dict:
        """Extract all information from the VariableRadiusFilletEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        edge_set_info = super().extract_info()
        variable_radius_info = {
            'start_radius': self.start_radius,
            'end_radius': self.end_radius,
            'mid_radii': self.mid_radii,
            'mid_positions': self.mid_positions,
        }
        return {**edge_set_info, **variable_radius_info}

"""
Constant Radius Fillet Edge Set Extractor Module

This module provides an extractor class for extracting information from ConstantRadiusFilletEdgeSet objects.

Classes:
    - ConstantRadiusFilletEdgeSetExtractor: Extractor for ConstantRadiusFilletEdgeSet objects.
"""
from typing import Optional, List, Dict
import adsk.fusion
import traceback
from .base_edge_set_extractor import BaseEdgeSetExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['ConstantRadiusFilletEdgeSetExtractor']

class ConstantRadiusFilletEdgeSetExtractor(BaseEdgeSetExtractor):
    """Extractor for extracting detailed information from ConstantRadiusFilletEdgeSet objects."""

    def __init__(self, element: adsk.fusion.ConstantRadiusFilletEdgeSet):
        """Initialize the extractor with the ConstantRadiusFilletEdgeSet element."""
        super().__init__(element)

    def extract_info(self) -> dict:
        """Extract all information from the ConstantRadiusFilletEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        edge_set_info = super().extract_info()
        constant_radius_info = {
            'radius': self.radius,
        }
        return {**edge_set_info, **constant_radius_info}

    @property
    def radius(self) -> Optional[str]:
        """Extracts the radius of the fillet edge set."""
        try:
            return nested_getattr(self._obj, 'radius.value', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting radius: {e}\n{traceback.format_exc()}')
            return None

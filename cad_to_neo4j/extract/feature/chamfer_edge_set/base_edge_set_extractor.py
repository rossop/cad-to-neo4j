"""
Base Edge Set Extractor Module

This module provides a base extractor class for extracting information from ChamferEdgeSet objects.

Classes:
    - BaseEdgeSetExtractor: Base extractor for ChamferEdgeSet objects.
"""

from typing import Optional, List
import adsk.fusion
import traceback
from ...base_extractor import BaseExtractor

__all__ = ['BaseEdgeSetExtractor']

class BaseEdgeSetExtractor(BaseExtractor):
    """Base extractor for extracting detailed information from ChamferEdgeSet objects."""

    def __init__(self, obj: adsk.fusion.ChamferEdgeSet):
        """Initialize the extractor with the ChamferEdgeSet element."""
        super().__init__(obj)

    @property
    def edges(self) -> Optional[List[str]]:
        """Extracts the IDs of edges associated with the chamfer edge set."""
        try:
            return [edge.entityToken for edge in self._obj.edges if edge.entityToken is not None]
        except AttributeError as e:
            self.logger.error(f'Error extracting edges: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> dict:
        """Extract all information from the ChamferEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        edge_set_info = super().extract_info()
        edge_info = {
            'edges': self.edges,
        }
        return {**edge_set_info, **edge_info}

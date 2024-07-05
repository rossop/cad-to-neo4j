"""
Base Edge Set Extractor Module

This module provides a base extractor class for extracting information from FilletEdgeSet objects.

Classes:
    - BaseEdgeSetExtractor: Base extractor for FilletEdgeSet objects.
"""
from typing import Optional, List, Dict
import adsk.fusion
import traceback
from ...base_extractor import BaseExtractor

__all__ = ['BaseEdgeSetExtractor']

class BaseEdgeSetExtractor(BaseExtractor):
    """Base extractor for extracting detailed information from FilletEdgeSet objects."""

    def __init__(self, element: adsk.fusion.FilletEdgeSet):
        """Initialize the extractor with the FilletEdgeSet element."""
        super().__init__(element)

    @property
    def edges(self) -> Optional[List[str]]:
        """Extracts the IDs of edges in the fillet edge set."""
        try:
            edge_collection = getattr(self._obj, 'edges', [])
            return [edge.entityToken for edge in edge_collection if getattr(edge, 'entityToken', None) is not None]
        except AttributeError as e:
            self.logger.error(f'Error extracting edges: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> dict:
        """Extract all information from the FilletEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        edge_set_info = {
            'edges': self.edges,
        }
        return edge_set_info

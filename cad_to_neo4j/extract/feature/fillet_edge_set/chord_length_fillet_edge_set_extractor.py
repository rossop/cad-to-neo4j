"""
Chord Length Fillet Edge Set Extractor Module

This module provides an extractor class for extracting information from ChordLengthFilletEdgeSet objects.

Classes:
    - ChordLengthFilletEdgeSetExtractor: Extractor for ChordLengthFilletEdgeSet objects.
"""
from typing import Optional, List, Dict
import adsk.fusion
import traceback
from .base_edge_set_extractor import BaseEdgeSetExtractor

__all__ = ['ChordLengthFilletEdgeSetExtractor']

class ChordLengthFilletEdgeSetExtractor(BaseEdgeSetExtractor):
    """Extractor for extracting detailed information from ChordLengthFilletEdgeSet objects."""

    def __init__(self, element: adsk.fusion.ChordLengthFilletEdgeSet):
        """Initialize the extractor with the ChordLengthFilletEdgeSet element."""
        super().__init__(element)

    def extract_info(self) -> dict:
        """Extract all information from the ChordLengthFilletEdgeSet element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        edge_set_info = super().extract_info()
        chordLength_info = {
            'chordLength': self.chordLength,
        }
        return {**edge_set_info, **chordLength_info}

    @property
    def chordLength(self) -> Optional[str]:
        """Extracts the chord length of the fillet edge set."""
        try:
            return getattr(self._obj, 'chordLength', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting chord length: {e}\n{traceback.format_exc()}')
            return None

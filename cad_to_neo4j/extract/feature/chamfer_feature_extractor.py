"""
Chamfer Feature Extractor Module

This module provides an extractor class for extracting information from ChamferFeature objects.

Classes:
    - ChamferFeatureExtractor: Extractor for ChamferFeature objects.
"""

from typing import Optional, List
import adsk.fusion
import traceback
from .feature_extractor import FeatureExtractor

__all__ = ['ChamferFeatureExtractor']

class ChamferFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from ChamferFeature objects."""

    def __init__(self, obj: adsk.fusion.ChamferFeature):
        """Initialize the extractor with the ChamferFeature element."""
        super().__init__(obj)

    @property
    def edge_sets(self) -> Optional[List[str]]:
        """Extracts the IDs of edge sets associated with the chamfer feature."""
        try:
            edge_set_id_list = []
            for edge_set in self._obj.edgeSets:
                pass
                # edge_set_id_list.append(edge_set.entityToken) # TODO get edge set IDs for further extraction
            return edge_set_id_list
        except AttributeError as e:
            self.logger.error(f'Error extracting edge sets: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> dict:
        """Extract all information from the ChamferFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        chamfer_info = {
            'edge_sets': self.edge_sets,
        }
        return {**feature_info, **chamfer_info}

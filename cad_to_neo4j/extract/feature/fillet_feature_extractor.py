"""
Fillet Feature Extractor Module

This module provides an extractor class for extracting information from FilletFeature objects.

Classes:
    - FilletFeatureExtractor: Extractor for FilletFeature objects.
"""
from typing import Optional, List, Dict
from adsk.fusion import FilletFeature
import traceback
from .feature_extractor import FeatureExtractor
from .fillet_edge_set.constant_radius_fillet_edge_set_extractor import ConstantRadiusFilletEdgeSetExtractor
from .fillet_edge_set.variable_radius_fillet_edge_set_extractor import VariableRadiusFilletEdgeSetExtractor
from .fillet_edge_set.chord_length_fillet_edge_set_extractor import ChordLengthFilletEdgeSetExtractor

__all__ = ['FilletFeatureExtractor']

class FilletFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from FilletFeature objects."""

    def __init__(self, element: FilletFeature):
        """Initialize the extractor with the FilletFeature element."""
        super().__init__(element)

    def extract_info(self) -> dict:
        """Extract all information from the FilletFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        fillet_info = {
            'filletedEdges': self.filletedEdges,
            'edge_set_id_list': self.edgeSets,
        }
        return {**feature_info, **fillet_info}

    @property
    def filletedEdges(self) -> Optional[List[str]]:
        """Extracts the IDs of edges modified by the fillet feature."""
        try:
            edgeSets = []
            for edge_set in getattr(self._obj, 'edgeSets', []):
                edges = [getattr(edge,'entityToken', None) for edge in getattr(edge_set, 'edges', None) if edge is not None]
                edgeSets += edges
            
            return edgeSets
        except AttributeError as e:
            self.logger.error(f'Error extracting edge sets: {e}\n{traceback.format_exc()}')
            return None

    @property
    def edgeSets(self) -> Optional[List[Dict[str, Optional[str]]]]:
        """Extracts the edge sets associated with the fillet feature."""
        edge_set_id_list = []
        try:
            for edge_set in getattr(self._obj,'edgeSets', []):
                if edge_set is not None:
                    pass
                    # edge_set_id_list.append(edge_set.entityToken) # TODO find a list of fillets in edgeset
                    # edge_set_id_list += [edge.entityToken for edge in edge_set]
        except AttributeError as e:
            self.logger.error(f'Error extracting edge sets: {e}\n{traceback.format_exc()}')
        return edge_set_id_list
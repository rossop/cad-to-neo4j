from typing import List, Dict, Any, Optional

import adsk.fusion

from .brep_entity_extractor import BRepEntityExtractor
from ...utils.extraction_utils import helper_extraction_error

__all__ = ['BRepEdgeExtractor']


class BRepEdgeExtractor(BRepEntityExtractor):
    """
    Extractor for BRepEdge data.
    """
    def __init__(self,
                 obj: adsk.fusion.BRepEdge,
                 design_environment_data: Dict[str, Any]):
        """
        Initialize the BRepEdgeExtractor with a BRepEdge object.

        Args:
            obj (adsk.fusion.BRepEdge): The BRepEdge object to extract data
            from.
        """
        super().__init__(obj, design_environment_data=design_environment_data)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract information from the BRepEdge object.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted information.
        """
        entity_info = super().extract_info()
        edge_info = {
            'startVertex': self.start_vertex,
            'endVertex': self.end_vertex,
            'isDegenerate': self.is_degenerate,
            'isTolerant': self.is_tolerant,
            'tolerance': self.tolerance,
            'faces': self.faces,
        }
        return {**entity_info, **edge_info}

    @property
    @helper_extraction_error
    def start_vertex(self) -> Optional[str]:
        """
        Extract the start vertex of the edge.

        Returns:
            Optional[str]: Entity token of the start vertex.
        """
        return self.extract_collection_tokens('startVertex', 'entityToken')

    @property
    @helper_extraction_error
    def end_vertex(self) -> Optional[str]:
        """
        Extract the end vertex of the edge.

        Returns:
            Optional[str]: Entity token of the end vertex.
        """
        return self.extract_collection_tokens('endVertex', 'entityToken')

    @property
    @helper_extraction_error
    def faces(self) -> List[str]:
        """
        Extract the BRepFaces that are associated with this edge through its
        BRepCoEdges.

        Returns:
            List[str]: List of entity tokens for the associated faces.
        """
        return self.extract_collection_tokens('faces', 'entityToken')

    @property
    @helper_extraction_error
    def is_degenerate(self) -> Optional[bool]:
        """
        Check if the edge's geometry is degenerate.

        Returns:
            Optional[bool]: True if the edge is degenerate, else False.
        """
        return getattr(self._obj, 'isDegenerate', None)

    @property
    @helper_extraction_error
    def is_tolerant(self) -> Optional[bool]:
        """
        Check if the edge is tolerant.

        Returns:
            Optional[bool]: True if the edge is tolerant, else False.
        """
        return getattr(self._obj, 'isTolerant', None)

    @property
    @helper_extraction_error
    def tolerance(self) -> Optional[float]:
        """
        Extract the tolerance value of the edge.

        Returns:
            Optional[float]: The tolerance value.
        """
        return getattr(self._obj, 'tolerance', None)

    @property
    @helper_extraction_error
    def point_on_edge(self) -> Optional[List[float]]:
        """
        Extract a sample point guaranteed to lie on the edge's curve.

        Returns:
            Optional[List[float]]: Coordinates of the sample point [x, y, z].
        """
        point = getattr(self._obj, 'pointOnEdge', None)
        return [point.x, point.y, point.z] if point else None

    @property
    @helper_extraction_error
    def co_edges(self) -> List[str]:
        """
        Extract the co-edges associated with the edge.

        Returns:
            List[str]: List of entity tokens for the associated co-edges.
        """
        return self.extract_collection_tokens('coEdges', 'entityToken')

    @property
    @helper_extraction_error
    def geometry(self) -> Optional[List[float]]:
        """
        Extract the geometry of the edge.

        Returns:
            Optional[List[float]]: Start and end points of the edge geometry.
        """
        geometry = getattr(self._obj, 'geometry', None)
        return [geometry.startPoint, geometry.endPoint] if geometry else None

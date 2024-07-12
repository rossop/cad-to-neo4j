import adsk.fusion  # TODO standardize this import
from .brep_entity_extractor import BRepEntityExtractor
from typing import List, Dict, Any, Optional

__all__ = ['BRepEdgeExtractor']

class BRepEdgeExtractor(BRepEntityExtractor):
    """
    Extractor for BRepEdge data.
    """
    def __init__(self, obj: adsk.fusion.BRepEdge):
        """
        Initialize the BRepEdgeExtractor with a BRepEdge object.

        Args:
            obj (adsk.fusion.BRepEdge): The BRepEdge object to extract data from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract information from the BRepEdge object.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted information.
        """
        entity_info = super().extract_info()
        edge_info = {
            'startVertex': self.startVertex,
            'endVertex': self.endVertex,
            'isDegenerate': self.isDegenerate,
            'isTolerant': self.isTolerant,
            'tolerance': self.tolerance,
            'faces': self.faces,
        }
        return {**entity_info, **edge_info}

    @property
    def startVertex(self) -> Optional[str]:
        """
        Extract the start vertex of the edge.

        Returns:
            Optional[str]: Entity token of the start vertex.
        """
        try:
            vertex = getattr(self._obj, 'startVertex', None)
            return getattr(vertex, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting startVertex: {e}")
            return None

    @property
    def endVertex(self) -> Optional[str]:
        """
        Extract the end vertex of the edge.

        Returns:
            Optional[str]: Entity token of the end vertex.
        """
        try:
            vertex = getattr(self._obj, 'endVertex', None)
            return getattr(vertex, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting endVertex: {e}")
            return None

    @property
    def faces(self) -> List[str]:
        """
        Extract the BRepFaces that are associated with this edge through its BRepCoEdges.

        Returns:
            List[str]: List of entity tokens for the associated faces.
        """
        try:
            faces = getattr(self._obj, 'faces', [])
            faces = [face.entityToken for face in faces]
            return faces
        except Exception as e:
            self.logger.error(f"Error extracting faces: {e}")
            return []

    @property
    def isDegenerate(self) -> Optional[bool]:
        """
        Check if the edge's geometry is degenerate.

        Returns:
            Optional[bool]: True if the edge is degenerate, else False.
        """
        try:
            return getattr(self._obj, 'isDegenerate', None)
        except Exception as e:
            self.logger.error(f"Error extracting isDegenerate: {e}")
            return None

    @property
    def isTolerant(self) -> Optional[bool]:
        """
        Check if the edge is tolerant.

        Returns:
            Optional[bool]: True if the edge is tolerant, else False.
        """
        try:
            return getattr(self._obj, 'isTolerant', None)
        except Exception as e:
            self.logger.error(f"Error extracting isTolerant: {e}")
            return None

    @property
    def tolerance(self) -> Optional[float]:
        """
        Extract the tolerance value of the edge.

        Returns:
            Optional[float]: The tolerance value.
        """
        try:
            return getattr(self._obj, 'tolerance', None)
        except Exception as e:
            self.logger.error(f"Error extracting tolerance: {e}")
            return None

    @property
    def pointOnEdge(self) -> Optional[List[float]]:
        """
        Extract a sample point guaranteed to lie on the edge's curve.

        Returns:
            Optional[List[float]]: Coordinates of the sample point [x, y, z].
        """
        try:
            point = getattr(self._obj, 'pointOnEdge', None)
            return [point.x, point.y, point.z] if point else None
        except Exception as e:
            self.logger.error(f"Error extracting pointOnEdge: {e}")
            return None

    @property
    def coEdges(self) -> List[str]:
        """
        Extract the co-edges associated with the edge.

        Returns:
            List[str]: List of entity tokens for the associated co-edges.
        """
        try:
            return [coEdge.entityToken for coEdge in getattr(self._obj, 'coEdges', []) if coEdge]
        except Exception as e:
            self.logger.error(f"Error extracting coEdges: {e}")
            return []

    @property
    def geometry(self) -> Optional[List[float]]:
        """
        Extract the geometry of the edge.

        Returns:
            Optional[List[float]]: Start and end points of the edge geometry.
        """
        try:
            geometry = getattr(self._obj, 'geometry', None)
            return [geometry.startPoint, geometry.endPoint] if geometry else None
        except Exception as e:
            self.logger.error(f"Error extracting geometry: {e}")
            return None

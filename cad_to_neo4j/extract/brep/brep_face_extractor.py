"""
BRep Face Extractor Module

This module provides an extractor class for extracting information from 
BRepFace objects, including their parent body and shell, and other 
properties.

Classes:
    - BRepFaceExtractor: Extractor for BRepFace objects.
"""
from typing import Optional, Dict, List, Any
import adsk.core
import adsk.fusion # TODO standardise this import for 
from .brep_entity_extractor import BRepEntityExtractor
from ...utils.extraction_utils import nested_getattr

__all__ = ['BRepFaceExtractor']

class BRepFaceExtractor(BRepEntityExtractor):
    """
    Extractor for BRepFace objects.

    This class provides methods to extract various properties from a BRepFace object.

    Attributes:
        shell (adsk.fusion.BRepFace): The BRep shell object to extract data from.
    """
    def __init__(self, obj: adsk.fusion.BRepFace):
        """Initializes the BRepShellExtractor with a BRepShell object.

        Args:
            obj: The BRep shell object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract BRepFace data."""
        entity_info = super().extract_info()
        face_info = {
            # 'shell' : self.shell,
            'tangentiallyConnectedFaces' : self.tangentiallyConnectedFaces,
            'edges': self.edges,

        }
        return {**entity_info, **face_info}

    @property
    def shell(self) -> Optional[str]:
        """
        Returns the parent shell of the face.

        Returns:
            Optional[str]: Entity token of the parent shell.
        """
        try:
            shell = getattr(self._obj, 'shell', None)
            return getattr(shell, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting shell: {e}")
            return None
    
    @property
    def geometry(self) -> Optional[str]:
        """
        Returns the underlying surface geometry of this face.

        Returns:
            Optional[str]: Entity token of the surface geometry.
        """
        try:
            geometry = getattr(self._obj, 'geometry', None)
            return getattr(geometry, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting geometry: {e}")
            return None

    @property
    def evaluator(self) -> Optional[str]:
        """
        Returns a SurfaceEvaluator to allow geometric evaluations across the face's surface.

        Returns:
            Optional[str]: Entity token of the surface evaluator.
        """
        try:
            evaluator = getattr(self._obj, 'evaluator', None)
            return getattr(evaluator, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting evaluator: {e}")
            return None

    @property
    def tangentiallyConnectedFaces(self) -> List[str]:
        """
        Returns the set of faces that are tangentially adjacent to this face.

        Returns:
            List[str]: List of entity tokens for tangentially connected faces.
        """
        try:
            tangential_faces = getattr(self._obj, 'tangentiallyConnectedFaces', [])
            return [face.entityToken for face in tangential_faces if getattr(face, 'entityToken', None) is not None]
        except Exception as e:
            self.logger.error(f"Error extracting tangentially connected faces: {e}")
            return []
        
    @property
    def edges(self) -> List[str]:
        """
        Extract the BRepEdges used by this face.

        Returns:
            List[str]: List of entity tokens for the associated edges.
        """
        try:
            edges = getattr(self._obj, 'edges', [])
            edges = [edge.entityToken for edge in edges]
            return edges
        except Exception as e:
            self.logger.error(f"Error extracting edges: {e}")
            return []
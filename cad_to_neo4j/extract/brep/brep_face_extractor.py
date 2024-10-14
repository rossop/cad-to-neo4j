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
import adsk.fusion

from .brep_entity_extractor import BRepEntityExtractor
from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error

__all__ = ['BRepFaceExtractor']


class BRepFaceExtractor(BRepEntityExtractor):
    """
    Extractor for BRepFace objects.

    This class provides methods to extract various properties from a BRepFace
    object.

    Attributes:
        shell (adsk.fusion.BRepFace): The BRep shell object to extract data
        from.
    """
    def __init__(self,
                 obj: adsk.fusion.BRepFace,
                 design_environment_data: Dict[str, Any]):
        """Initializes the BRepShellExtractor with a BRepShell object.

        Args:
            obj: The BRep shell object to extract information from.
        """
        super().__init__(obj, design_environment_data=design_environment_data)

    def extract_info(self) -> Dict[str, Any]:
        """Extract BRepFace data."""
        entity_info = super().extract_info()
        face_info = {
            # 'shell' : self.shell,
            'tangentiallyConnectedFaces': self.tangentially_connected_faces,
            'edges': self.edges,

        }
        return {**entity_info, **face_info}

    @property
    @helper_extraction_error
    def shell(self) -> Optional[str]:
        """
        Returns the parent shell of the face.

        Returns:
            Optional[str]: Entity token of the parent shell.
        """
        return nested_getattr(self._obj, 'shell.entityToken', None)

    @property
    @helper_extraction_error
    def geometry(self) -> Optional[str]:
        """
        Returns the underlying surface geometry of this face.

        Returns:
            Optional[str]: Entity token of the surface geometry.
        """
        return nested_getattr(self._obj, 'geometry.entityToken', None)

    @property
    @helper_extraction_error
    def evaluator(self) -> Optional[str]:
        """
        Returns a SurfaceEvaluator to allow geometric evaluations across the
        face's surface.

        Returns:
            Optional[str]: Entity token of the surface evaluator.
        """
        return nested_getattr(self._obj, 'evaluator.entityToken', None)

    @property
    @helper_extraction_error
    def tangentially_connected_faces(self) -> List[str]:
        """
        Returns the set of faces that are tangentially adjacent to this face.

        Returns:
            List[str]: List of entity tokens for tangentially connected faces.
        """
        return self.extract_collection_tokens(
            'tangentiallyConnectedFaces', 'entityToken')

    @property
    @helper_extraction_error
    def edges(self) -> List[str]:
        """
        Extract the BRepEdges used by this face.

        Returns:
            List[str]: List of entity tokens for the associated edges.
        """
        return self.extract_collection_tokens('edges', 'entityToken')

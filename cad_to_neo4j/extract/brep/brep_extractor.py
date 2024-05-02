"""
BRep Extractor Module

This module provides an extractor class for extracting information from 
Boundary Representations object including BRep entities such as faces, 
edges, and vertices.

Classes:
    - BRepExtractor: Extractor for BRep objects.
    - BRepEntityExtractor: Base class for BRep entities.
    - BRepFaceExtractor: Extractor for BRepFace objects.
    - BRepEdgeExtractor: Extractor for BRepEdge objects.
"""
import adsk.fusion # TODO standardise this import for 
from ..base_extractor import BaseExtractor

__all__ = ['BRepExtractor','BRepEntityExtractor', 'BRepFaceExtractor', 'BRepEdgeExtractor']

class BRepExtractor(BaseExtractor):
    """Extractor for BRep data from bodies and features."""
    def __init__(self, obj: adsk.fusion.BRepBody):
        """Initialize the extractor with the Feature element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract BRep data from the body or feature."""
        basic_info = super().extract_info()
        brep_data = {}
        return {**brep_data, **basic_info}

class BRepEntityExtractor(BaseExtractor):
    """Base extractor for BRep entities."""
    def __init__(self, obj: adsk.fusion.Base):
        """Initialize the extractor with the BRepEntity element."""
        super().__init__(obj)

class BRepFaceExtractor(BRepEntityExtractor):
    """Extractor for BRepFace data."""
    def __init__(self, obj: adsk.fusion.BRepFace):
        """Initialize the extractor with the BRepFace element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract BRepFace data."""
        entity_info = super().extract_info()
        face_info = {}
        return {**entity_info, **face_info}

class BRepEdgeExtractor(BRepEntityExtractor):
    """Extractor for BRepEdge data."""
    def __init__(self, obj: adsk.fusion.BRepEdge):
        """Initialize the extractor with the BRepEdge element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract BRepEdge data."""
        entity_info = super().extract_info()
        face_info = {}
        return {**entity_info, **face_info}
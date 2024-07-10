"""
BRep Extractor Module

This module provides an extractor class for extracting information from 
Boundary Representation (BRep) objects including BRep entities such as faces, 
edges, and vertices.

Classes:
    - BRepBodyExtractor: Extractor for BRep objects.
    - BRepEntityExtractor: Base class for BRep entities.
    - BRepLumpExtractor: Extractor for BRepLump objects.
    - BRepShellExtractor: Extractor for BRepShell objects.
    - BRepFaceExtractor: Extractor for BRepFace objects.
    - BRepEdgeExtractor: Extractor for BRepEdge objects.
    - BRepVertexExtractor: Extractor for BRepVertex objects.
"""

from .brep_extractor import BRepBodyExtractor

from .brep_entity_extractor import BRepEntityExtractor
from .brep_vertex_extractor import BRepVertexExtractor
from .brep_edge_extractor import BRepEdgeExtractor
from .brep_face_extractor import BRepFaceExtractor
from .brep_lump_extractor import BRepLumpExtractor
from .brep_shell_extractor import BRepShellExtractor


__all__ = ['BRepBodyExtractor', 'BRepEntityExtractor', 'BRepLumpExtractor', 'BRepShellExtractor', 'BRepFaceExtractor', 'BRepEdgeExtractor', 'BRepVertexExtractor']

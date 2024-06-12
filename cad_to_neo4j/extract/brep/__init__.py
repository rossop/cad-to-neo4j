"""
BRep Extractor Module

This module provides an extractor class for extracting information from 
Boundary Representation (BRep) objects including BRep entities such as faces, 
edges, and vertices.

Classes:
    - BRepExtractor: Extractor for BRep objects.
    - BRepEntityExtractor: Base class for BRep entities.
    - BRepFaceExtractor: Extractor for BRepFace objects.
    - BRepEdgeExtractor: Extractor for BRepEdge objects.
"""

from .brep_extractor import BRepExtractor, BRepEntityExtractor, BRepEdgeExtractor, BRepFaceExtractor

__all__ = ['BRepExtractor', 'BRepEntityExtractor', 'BRepFaceExtractor', 'BRepEdgeExtractor']

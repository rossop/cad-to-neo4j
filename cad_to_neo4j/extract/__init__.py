"""
Extraction Module

This module contains classes and functions for extracting various properties and information 
from CAD objects. It serves as the extraction part of the ELT (Extract, Load, Transform) pipeline 
for processing CAD models and storing them in a Neo4j graph database.

Modules:
    - base_extractor.py: Provides the BaseExtractor class for extracting basic properties such as 
      name, type, and id token from CAD objects.
    - feature_extractor.py: Provides the FeatureExtractor class for extracting properties specific 
      to feature objects in CAD models.
    - sketch_extractor.py: Provides the SketchExtractor class for extracting properties specific 
      to sketch objects in CAD models.
    - brep_extractor.py: Provides the BRepExtractor class for extracting properties specific 
      to BRep (Boundary Representation) objects in CAD models.
    - extractor_factory.py: Provides the factory function to get the appropriate extractor based 
      on the type of CAD object, and functions for extracting data from components.

Classes:
    - BaseExtractor: Base class for all extractors, extracting common properties.
    - SketchExtractor: Extractor for Sketch objects, inheriting from BaseExtractor.
    - FeatureExtractor: Extractor for Feature objects, inheriting from BaseExtractor.
    - BRepExtractor: Extractor for BRep objects, inheriting from BaseExtractor.
    - get_extractor: Factory function to get the appropriate extractor for a given CAD object.
    - extract_data: Function to extract data from a CAD object.
    - extract_component_data: Function to extract data from components in a CAD design.
    # TODO refactor isolating the modules
"""

from .base_extractor import BaseExtractor
from .sketch_extractor import SketchExtractor, SketchPointExtractor, SketchCurveExtractor, SketchDimensionExtractor
from .feature_extractor import FeatureExtractor
from .brep_extractor import BRepExtractor, BRepEntityExtractor, BRepFaceExtractor, BRepEdgeExtractor
from .extractor_factory import get_extractor, extract_data, extract_component_data

__all__ = ['BaseExtractor', 'SketchExtractor', 'SketchPointExtractor', 'SketchCurveExtractor', 'SketchDimensionExtractor', 'ProfileExtractor', 'FeatureExtractor', 'BRepExtractor', 'get_extractor', 'extract_data', 'extract_component_data', 'BRepEntityExtractor', 'BRepFaceExtractor', 'BRepEdgeExtractor']
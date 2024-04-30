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
"""

from . import base_extractor
from . import sketch_extractors
from . import feature_extractor
from . import brep_extractor
from .extractor_factory import *

__all__ = (
    base_extractor.__all__ + 
    sketch_extractors.__all__ + 
    feature_extractor.__all__ + 
    brep_extractor.__all__ + 
    extractor_factory.__all__
    )
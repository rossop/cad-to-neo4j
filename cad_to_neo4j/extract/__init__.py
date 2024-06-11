"""
Extraction Module

This module contains classes and functions for extracting various properties and information 
from CAD objects. It serves as the extraction part of the ELT (Extract, Load, Transform) pipeline 
for processing CAD models and storing them in a Neo4j graph database.

Modules:
    - base_extractor.py: Provides the BaseExtractor class for extracting basic properties such as 
      name, type, and id token from CAD objects.
    - feature: Provides the FeatureExtractor class for extracting properties specific 
      to feature objects in CAD models.
    - sketch: Provides the SketchExtractor class for extracting properties specific 
      to sketch objects in CAD models.
    - brep: Provides the BRepExtractor class for extracting properties specific 
      to BRep (Boundary Representation) objects in CAD models.
    - extractor.py: Provides the factory function to get the appropriate extractor based 
      on the type of CAD object, and functions for extracting data from components.
"""

from . import base_extractor
from . import sketch
from . import feature
from . import brep
from . import construction_plane_extractor
from .extractor import *

__all__ = (
    base_extractor.__all__ + 
    sketch.__all__ + 
    feature.__all__ + 
    brep.__all__ + 
    extractor.__all__ +
    construction_plane_extractor.__all__
    )
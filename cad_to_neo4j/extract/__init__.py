"""
Extraction Module

This package contains modules and classes for extracting various properties 
and information from CAD objects. It serves as the extraction part of the 
ETL (Extract, Transform, Load) pipeline for processing CAD models and 
storing them in a Neo4j graph database.

Modules:
    - base_extractor.py: Provides the BaseExtractor class for extracting 
      basic properties such as name, type, and id token from CAD objects.
    - feature_extractor.py:
    - sketch_extractor.py:
    - extractor_factory.py:

Classes:
    - BaseExtractor: Base class for all extractors.
    - SketchExtractor: Extractor for Sketch objects.
    - FeatureExtractor: Extractor for Feature objects.
    - get_extractor: Factory function to get the appropriate extractor.
"""


from .base_extractor import BaseExtractor
from .sketch_extractor import SketchExtractor
from .feature_extractor import FeatureExtractor
from .extractor_factory import get_extractor

__all__ = ['BaseExtractor', 'SketchExtractor', 'FeatureExtractor', 'get_extractor']
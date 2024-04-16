"""
Extraction Package

This package contains modules and classes for extracting various properties 
and information from CAD objects. It serves as the extraction part of the 
ETL (Extract, Transform, Load) pipeline for processing CAD models and 
storing them in a Neo4j graph database.

Modules:
    - base_extractor.py: Provides the BaseExtractor class for extracting 
      basic properties such as name, type, and id token from CAD objects.
"""

from .base_extractor import *

__all__ = base_extractor.__all__
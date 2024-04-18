"""
CAD to Neo4j Package

This package provides an ELT (Extract, Load, Transform) pipeline for processing CAD models 
from Autodesk Fusion 360 and storing them in a Neo4j graph database. The pipeline consists 
of extraction of CAD model data, loading the extracted data into the Neo4j database, and 
optional transformation of data for further analysis.

Modules:
    - extract: Contains modules and classes for extracting various properties and information 
      from CAD objects.
    - load: Provides functionalities for loading data into the Neo4j graph database.
    - transform: (Future implementation) Contains modules and classes for transforming data.
    - utils: Common utility functions and classes used across the package.
"""

from .utils import *
from .extract import *
from .load import *

__all__ = utils.__all__ + extract.__all__ + load.__all__
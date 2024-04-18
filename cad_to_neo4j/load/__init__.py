"""
Load Module

This module provides functionalities for loading data into the Neo4j graph database. It includes 
modules for establishing connections and inserting nodes and relationships into the database, 
serving as the loading part of the ELT (Extract, Load, Transform) pipeline for processing CAD models.

Modules:
    - neo4j_loader.py: Contains the Neo4jLoader class and functions for interacting with the Neo4j 
      database, including creating nodes and relationships.
"""

from .neo4j_loader import Neo4jLoader

__all__ = ['Neo4jLoader']

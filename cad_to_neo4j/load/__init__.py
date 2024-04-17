"""
Load Package

This package provides functionalities for loading data into the Neo4j graph database.
It includes modules for establishing connections and inserting nodes and relationships
into the database.

Modules:
    - neo4j_loader.py: Functions for interacting with the Neo4j database, including
      creating nodes and relationships.
"""

from .neo4j_loader import Neo4jLoader

__all__ = ['Neo4jLoader']

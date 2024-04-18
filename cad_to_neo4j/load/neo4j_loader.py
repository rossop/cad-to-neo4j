"""
Neo4j Loader Module

This module provides functions to load CAD data into a Neo4j graph database.

Functions:
    - create_nodes: Creates multiple nodes in the Neo4j database.
    - create_relationships: Creates multiple relationships between nodes in the Neo4j database.
    - load_data: Loads extracted data into the Neo4j database.
"""

from neo4j import GraphDatabase
from typing import Dict, List, Union
import logging

__all__ = ['Neo4jLoader', 'create_nodes', 'create_relationships', 'load_data']

class Neo4jLoader(object):
    """
    A class to handle loading data into a Neo4j graph database.

    Attributes:
        driver (neo4j.GraphDatabase.driver): The Neo4j driver for database connections.
        _batch_size (int): The size of batches for bulk data loading.
        logger (logging.Logger): The logger for logging messages and errors.
    """
    def __init__(self, uri: str, user: str, password: str, Logger: logging.Logger = None ):
        """
        Initialises the Neo4jLoader with the provided database credentials.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
            Logger (logging.Logger, optional): The logger for logging messages and errors.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._batch_size = 1000
        self.logger = Logger 

    def close(self):
        """
        Closes the Neo4j driver connection and sets the logger to None.
        """
        # Clean up the Neo4j driver connection
        if self.driver:
            self.driver.close()
        # Set the logger to None
        self.Logger = None
    
    def __enter__(self):
        """
        Enters the runtime context related to this object.
        
        Returns:
            Neo4jLoader: The instance of Neo4jLoader.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the runtime context related to this object.
        
        Ensures resources are cleaned up.
        """
        self.close()

    def create_nodes(self, tx, nodes: List[Dict]):
        """Creates multiple nodes in the Neo4j database in a batch.

        Args:
            tx: The transaction object.
            nodes (list): List of node dictionaries.
        """
        try:
            query = """
            UNWIND $nodes AS node
            CALL apoc.create.node([node.type], node.properties) YIELD node AS created_node
            RETURN created_node
            """
            tx.run(query, nodes=nodes)
            self.logger.info(f"Created {len(nodes)} nodes")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating nodes: {e}")

    def create_relationships(self, tx, relationships: List[Dict]):
        """Creates multiple relationships in the Neo4j database in a batch.

        Args:
            tx: The transaction object.
            relationships (list): List of relationship dictionaries.
        """
        try:
            if self.logger:
                self.logger.debug(f"{relationships}")
            query = """
            UNWIND $relationships AS rel
            MATCH (a {id_token: rel.from_id}), (b {id_token: rel.to_id})
            CALL apoc.create.relationship(a, rel.rel_type, {}, b) YIELD rel as created_rel
            RETURN created_rel
            """
            tx.run(query, relationships=relationships)
            if self.logger:
                self.logger.info(f"Created {len(relationships)} relationships")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating relationships: {e}")
        
    def load_data(self, nodes: Union[Dict, List[Dict]], relationships: List[Dict] = None):
        """Loads extracted data into the Neo4j database.

        Args:
            nodes (list): The extracted node data.
            relationships (list): The extracted relationship data.
        """
        if isinstance(nodes, dict):
            nodes = [nodes]

        try:
            # Create nodes in batches
            with self.driver.session() as session:
                if nodes:
                    for i in range(0, len(nodes), self._batch_size):
                        self.logger.info(f"Loading batch {i // self._batch_size + 1} with {len(nodes[i:i + self._batch_size])} nodes")
                        session.write_transaction(self.create_nodes, nodes[i:i + self._batch_size])

                # Create relationships in batches
                if relationships:
                    for i in range(0, len(relationships), self._batch_size):
                        self.logger.info(f"Loading batch {i // self._batch_size + 1} with {len(relationships[i:i + self._batch_size])} relationships")
                        session.write_transaction(self.create_relationships, relationships[i:i + self._batch_size])

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading data: {e}")

# Usage example
if __name__ == "__main__":
    # Imports only relevant to this example
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env file
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    # Neo4j credentials
    NEO4J_URI = os.getenv('NEO4J_URI')
    NEO4J_USER = os.getenv('NEO4J_USER')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')


    Loader = Neo4jLoader(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
    
    # Example data to load
    data = [
        {'type': 'Sketch', 'properties': {'id_token': 'id1', 'name': 'Sketch1'}},
        {'type': 'Feature', 'properties': {'id_token': 'id2', 'name': 'Extrude1'}},
        # Add more data as needed
    ]
    Loader.load_data(data)
    Loader.close()

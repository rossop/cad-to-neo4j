"""
Neo4j Loader Module

This module provides functions to load CAD data into a Neo4j graph database.

Functions:
    - create_nodes: Creates multiple nodes in the Neo4j database.
    - create_relationships: Creates multiple relationships between nodes in the Neo4j database.
    - load_data: Loads extracted data into the Neo4j database.
"""

from ..utils.neo4j_utils import Neo4jTransactionManager
from typing import Dict, List, Union
import logging
import traceback

__all__ = ['Neo4jLoader']

class Neo4jLoader(Neo4jTransactionManager):
    """
    A class to handle loading data into a Neo4j graph database.

    Attributes:
        driver (neo4j.GraphDatabase.driver): The Neo4j driver for database connections.
        _batch_size (int): The size of batches for bulk data loading.
        logger (logging.Logger): The logger for logging messages and errors.
    
    Methods:
        create_nodes(tx, nodes): Creates multiple nodes in the Neo4j database in a batch.
        create_relationships(tx, relationships): Creates multiple relationships in the Neo4j database in a batch.
        load_data(nodes, relationships=None): Loads extracted data into the Neo4j database.
    """
    def __init__(self, uri: str, user: str, password: str, logger: logging.Logger = None, max_retries: int = 5, timeout: int = 5):
        """
        Initialises the Neo4jLoader with the provided database credentials.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
            logger (logging.Logger, optional): The logger for logging messages and errors.
            max_retries (int, optional): The maximum number of retries for connecting to the database. Defaults to 5.
            timeout (int, optional): The timeout in seconds between retries. Defaults to 5.
        """
        super().__init__(uri, user, password, logger, max_retries, timeout)
        self._batch_size: int = 1000  

    @property
    def batch_size(self):
        """Gets the batch size for bulk data loading."""
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: int):
        """Sets the batch size for bulk data loading."""
        if value > 0:
            self._batch_size = value
        else:
            raise ValueError("Batch size must be a positive integer")

    def clear(self):
        """Clears all nodes and relationships in the Neo4j database."""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (n) DETACH DELETE n
                """
                session.write_transaction(lambda tx: tx.run(query))
                self.logger.info("Cleared Database")
        except Exception as e:
            self.logger.error(f"Failed to clear database:\n{traceback.format_exc()}")

    def create_nodes(self, tx, nodes: List[Dict]):
        """Creates multiple nodes in the Neo4j database in a batch.

        Args:
            tx: The transaction object.
            nodes (list): List of node dictionaries.
        """
        try:
            query = """
            UNWIND $nodes AS node
            CALL apoc.create.node(node.type, node) YIELD node AS created_node
            RETURN created_node
            """
            tx.run(query, nodes=nodes)
            self.logger.info(f"Created {len(nodes)} nodes")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed:\n{traceback.format_exc()}")

    def create_relationships(self, tx, relationships: List[Dict]):
        """Creates multiple relationships in the Neo4j database in a batch.

        Args:
            tx: The transaction object.
            relationships (list): List of relationship dictionaries.
        """
        try:
            query = """
            UNWIND $relationships AS rel
            MATCH (a {entityToken: rel.from_id}), (b {entityToken: rel.to_id})
            CALL apoc.create.relationship(a, rel.rel_type, {}, b) YIELD rel as created_rel
            RETURN created_rel
            """
            tx.run(query, relationships=relationships)
            if self.logger:
                self.logger.info(f"Created {len(relationships)} relationships")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed:\n{traceback.format_exc()}")
        
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
            if nodes:
                for i in range(0, len(nodes), self.batch_size):
                    self.logger.info(f"Loading batch {i // self.batch_size + 1} with {len(nodes[i:i + self.batch_size])} nodes")
                    self.session.write_transaction(self.create_nodes, nodes[i:i + self.batch_size])

            # Create relationships in batches
            if relationships:
                for i in range(0, len(relationships), self.batch_size):
                    self.logger.info(f"Loading batch {i // self.batch_size + 1} with {len(relationships[i:i + self.batch_size])} relationships")
                    self.session.write_transaction(self.create_relationships, relationships[i:i + self.batch_size])
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed:\n{traceback.format_exc()}")

# Usage example
if __name__ == "__main__":
    # Imports only relevant to this example
    import os
    from ..utils.credential_utils import load_credentials

    # Load environment variables from .env file
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    credentials = load_credentials(dotenv_path=dotenv_path)

    # Neo4j credentials
    NEO4J_URI = credentials["NEO4J_URI"]
    NEO4J_USER = credentials["NEO4J_USER"]
    NEO4J_PASSWORD = credentials["NEO4J_PASSWORD"]

    Loader = Neo4jLoader(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
    
    # Example data to load
    data = [
        {'type': 'Sketch', 'entityToken': 'id1', 'name': 'Sketch1'},
        {'type': 'Feature', 'entityToken': 'id2', 'name': 'Extrude1'},
        # Add more data as needed
    ]
    Loader.load_data(data)
    Loader.close()
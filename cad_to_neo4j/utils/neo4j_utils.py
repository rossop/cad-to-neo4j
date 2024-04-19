"""
Neo4j Transaction Manager Utilities

This module provides a utility class for managing Neo4j transactions.
It includes methods to execute Cypher queries and handle the lifecycle of the Neo4j driver.

Classes:
    - Neo4jTransactionManager: Manages Neo4j transactions and driver lifecycle.
"""

from neo4j import GraphDatabase

__all__ = ['Neo4jTransactionManager']

class Neo4jTransactionManager(object):
    """
    A class to manage Neo4j transactions, providing methods to execute Cypher queries
    and handle the lifecycle of the Neo4j driver.

    Attributes:
        driver (neo4j.GraphDatabase.driver): The Neo4j driver for database connections.

    Methods:
        close(): Closes the Neo4j driver connection.
        __enter__(): Enters the runtime context related to this object.
        __exit__(exc_type, exc_value, traceback): Exits the runtime context related to this object.
        execute_query(query, parameters=None): Executes a Cypher query and returns the results.
    """
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialises the Neo4jTransactionManager with the provided database credentials.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self.driver:
            self.driver.close()

    def __enter__(self):
        """
        Enters the runtime context related to this object.

        Returns:
            Neo4jTransactionManager: The instance of Neo4jTransactionManager.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the runtime context related to this object, ensuring the driver connection is closed.

        Args:
            exc_type (type): The exception type.
            exc_value (Exception): The exception instance.
            traceback (traceback): The traceback object.
        """
        self.close()

    def execute_query(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query and returns the results.

        Args:
            query (str): The Cypher query to execute.
            parameters (dict, optional): The parameters for the Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return result.values()

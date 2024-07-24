"""
Neo4j Transaction Manager Utilities

This module provides a utility class for managing Neo4j transactions.
It includes methods to execute Cypher queries and handle the lifecycle of the Neo4j driver.

Classes:
    - Neo4jTransactionManager: Manages Neo4j transactions and driver lifecycle.
"""

from neo4j import GraphDatabase, exceptions
import logging
import time

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
    def __init__(self, uri: str, user: str, password: str, logger: logging.Logger = None, max_retries: int = 5, timeout: int = 5):
        """
        Initialises the Neo4jTransactionManager with the provided database credentials.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
            logger (logging.Logger, optional): The logger for logging messages and errors. Defaults to None.
            max_retries (int, optional): The maximum number of retries for connecting to the database. Defaults to 5.
            timeout (int, optional): The timeout in seconds between retries. Defaults to 5.
        """
        self.logger = logger if logger else logging.getLogger(__name__)
        self.max_retries = max_retries
        self.timeout = timeout
        self.driver = None
        self.connect(uri, user, password)

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
        self.session = self.driver.session()
        return self

    def __exit__(self, *args):
        """
        Exits the runtime context related to this object, ensuring the driver connection is closed.

        Args:
            *args: The exception type, value, and traceback.
        """
        self.session.close()
        self.close()

    def connect(self, uri: str, user: str, password: str):
        """
        Attempts to connect to the Neo4j database with retries.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                self.logger.info("Successfully connected to Neo4j")
                return
            except exceptions.ServiceUnavailable as e:
                self.logger.error(f"Connection attempt {retries + 1} failed: {e}")
                retries += 1
                time.sleep(self.timeout)
        self.logger.error("Max retries reached. Could not connect to Neo4j")

    def execute_query(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query and returns the results.

        Args:
            query (str): The Cypher query to execute.
            parameters (dict, optional): The parameters for the Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        try:
            result = self.session.run(query, parameters)
            return result.values()
        except Exception as e:
            self.logger.error(f'Error executing query: {e}')
            raise

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"

    with Neo4jTransactionManager(uri, user, password) as manager:
        query = "MATCH (n) RETURN n LIMIT 10"
        results = manager.execute_query(query)
        if results:
            for record in results:
                print(record)
"""
Neo4j Transformer Orchestrator Module

This module provides a class orchestrating other transformation classes used to
transform CAD data in a Neo4j graph database.

Classes:
    - Neo4jTransformer: A class to handle transformations in a Neo4j graph
      database.
"""

from ..utils.neo4j_utils import Neo4jTransactionManager
import logging

from ..utils.cypher_utils import helper_cypher_error

from .core.strategies import (
    BRepTransformer,
    ComponentTransformer,
    ConstructionElementsTransformer,
    FeatureTransformer,
    ProfileTransformer,
    SketchTransformer,
    TimelineTransformer,
    ParameterTransformer
    )

__all__ = ['Neo4jTransformerOrchestrator']


class Neo4jTransformerOrchestrator(Neo4jTransactionManager):
    """
    A class to orchestrate all transformations in a Neo4j graph database.

    Attributes:
        driver (neo4j.GraphDatabase.driver): The Neo4j driver for database
            connections.
        logger (logging.Logger): The logger for logging messages and errors.
        transformers (list): A list of transformer instances.

    Methods:
        __init__(uri, user, password, logger): Initialises the transformer
            with database credentials and sub-transformers.
        execute_query(query): Executes a Cypher query on the Neo4j database.
        execute(): Runs all transformation methods to create relationships in
            the model.
    """
    def __init__(
            self,
            uri: str,
            user: str,
            password: str,
            logger: logging.Logger = None,
            max_retries: int = 5,
            timeout: int = 5):
        """
        Initializes the Neo4jTransformer with the provided database
        credentials.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
            logger (logging.Logger, optional): The logger for logging messages
                and errors.
            max_retries (int, optional): The maximum number of retries for
                connecting to the database. Defaults to 5.
            timeout (int, optional): The timeout in seconds between retries.
                Defaults to 5.
        """
        super().__init__(uri, user, password, logger, max_retries, timeout)
        self.transformers = [
            BRepTransformer(self.logger),
            ComponentTransformer(self.logger),
            ConstructionElementsTransformer(self.logger),
            FeatureTransformer(self.logger),
            ProfileTransformer(self.logger),
            TimelineTransformer(self.logger),
            SketchTransformer(self.logger),
            ParameterTransformer(self.logger),
        ]

    @helper_cypher_error
    def execute(self):
        """
        Run all transformation methods to create relationships in the model.

        Returns:
            dict: Results of all transformations.
        """
        results = {}
        self.logger.info('Running all transformations...')

        # Execute timeline transformations
        for t in self.transformers:
            info_msg: str = \
                f'Executing {t.__class__.__name__} transformations...'
            self.logger.info(info_msg)
            results[t.__class__.__name__] = t.transform(self.execute_query)

        return results


# Usage example
if __name__ == "__main__":
    import os
    from ..utils.credential_utils import load_credentials

    # Load environment variables from .env file
    dotenv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '.env')
    credentials = load_credentials(dotenv_path=dotenv_path)

    # Neo4j credentials
    NEO4J_URI = credentials["NEO4J_URI"]
    NEO4J_USER = credentials["NEO4J_USER"]
    NEO4J_PASSWORD = credentials["NEO4J_PASSWORD"]

    transformer = Neo4jTransformerOrchestrator(
        NEO4J_URI,
        NEO4J_USER,
        NEO4J_PASSWORD)
    try:
        nodes = transformer.create_timeline_relationships()
        for record in nodes:
            print(record)
        transformer.create_face_adjacencies()
    finally:
        transformer.close()

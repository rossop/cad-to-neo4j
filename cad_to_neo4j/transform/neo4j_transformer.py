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
import traceback 

from .core.strategies import (
    BRepTransformer,
    ComponentTransformer,
    ConstructionElementsTransformer,
    FeatureTransformer,
    ProfileTransformer,
    SketchTransformer,
    TimelineTransformer,
    )

__all__ = ['Neo4jTransformerOrchestrator']

class Neo4jTransformerOrchestrator(Neo4jTransactionManager):
    """
    A class to orchestrate all transformations in a Neo4j graph database.

    Attributes:
        driver (neo4j.GraphDatabase.driver): The Neo4j driver for database connections.
        logger (logging.Logger): The logger for logging messages and errors.
        transformers (list): A list of transformer instances.
    
    Methods:
        __init__(uri, user, password, logger): Initialises the transformer with database credentials and sub-transformers.
        execute_query(query): Executes a Cypher query on the Neo4j database.
        execute(): Runs all transformation methods to create relationships in the model.
        create_timeline_relationships(): Creates relationships between nodes based on their timeline index.
        create_profile_relationships(): Creates 'USES_PROFILE' relationships between extrusions and profiles.
        create_adjacent_face_relationships(): Creates 'ADJACENT' relationships between faces sharing the same edge.
        create_adjacent_edge_relationships(): Creates 'ADJACENT' relationships between edges sharing the same vertex.
        create_sketch_relationships(): Creates various relationships between sketch entities.
    """
    def __init__(self, uri: str, user: str, password: str, Logger: logging.Logger = None):
        """
        Initializes the Neo4jTransformer with the provided database credentials.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
            logger (logging.Logger, optional): The logger for logging messages and errors.
        """
        super().__init__(uri, user, password)
        self.logger = Logger
        self.transformers = [
            BRepTransformer(self.logger),
            ComponentTransformer(self.logger),
            ConstructionElementsTransformer(self.logger),
            FeatureTransformer(self.logger),
            ProfileTransformer(self.logger),
            TimelineTransformer(self.logger),
            SketchTransformer(self.logger),
        ]

    def execute(self):
        """
        Run all transformation methods to create relationships in the model.
        
        Returns:
            dict: Results of all transformations.
        """
        results = {}
        self.logger.info('Running all transformations...')

        # Execute timeline transformations
        for transformer in self.transformers:
            try:
                self.logger.info(f'Executing {transformer.__class__.__name__} transformations...')
                results[transformer.__class__.__name__] = transformer.transform(self.execute_query)
            except Exception as e:
                self.logger.error(f'Exception in {transformer.__class__.__name__}: {e}\n{traceback.format_exc()}')
                
        return results

# Usage example
if __name__ == "__main__":
    import os
    from ..utils.credential_utils import load_credentials

    # Load environment variables from .env file
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    credentials = load_credentials(dotenv_path=dotenv_path)

    # Neo4j credentials
    NEO4J_URI = credentials["NEO4J_URI"]
    NEO4J_USER = credentials["NEO4J_USER"]
    NEO4J_PASSWORD = credentials["NEO4J_PASSWORD"]

    transformer = Neo4jTransformerOrchestrator(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        nodes = transformer.create_timeline_relationships()
        for record in nodes:
            print(record)
        transformer.create_face_adjacencies()
    finally:
        transformer.close()

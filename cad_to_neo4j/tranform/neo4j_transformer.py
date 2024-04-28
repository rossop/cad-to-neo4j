"""
Neo4j Transformer Module

This module provides functions to transform CAD data in a Neo4j graph database.

Classes:
    - Neo4jTransformer: A class to handle transformations in a Neo4j graph database.
"""

from ..utils.neo4j_utils import Neo4jTransactionManager
import logging

__all__ = ['Neo4jTransformer']

class Neo4jTransformer(Neo4jTransactionManager):
    """
    A class to handle transformations in a Neo4j graph database.

    Attributes:
        driver (neo4j.GraphDatabase.driver): The Neo4j driver for database connections.
        logger (logging.Logger): The logger for logging messages and errors.
    
    Methods:
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

    def execute(self):
        """
        Run all transformation methods to create relationships in the model.
        
        Returns:
            dict: Results of all transformations.
        """
        results = {}
        
        self.logger.info('Running all transformations...')
        
        try:
            results['timeline_relationships'] = self.create_timeline_relationships()
        except Exception as e:
            self.logger.error(f'Exception in creating timeline relationships: {e}')
        
        try:
            results['profile_relationships'] = self.create_profile_relationships()
        except Exception as e:
            self.logger.error(f'Exception in creating profile relationships: {e}')
        
        try:
            results['adjacent_face_relationships'] = self.create_adjacent_face_relationships()
        except Exception as e:
            self.logger.error(f'Exception in creating adjacent face relationships: {e}')
        
        try:
            results['adjacent_edge_relationships'] = self.create_adjacent_edge_relationships()
        except Exception as e:
            self.logger.error(f'Exception in creating adjacent edge relationships: {e}')
        
        try:
            results['sketch_relationships'] = self.create_sketch_relationships()
        except Exception as e:
            self.logger.error(f'Exception in creating sketch relationships: {e}')
        
        return results

    def create_timeline_relationships(self):
        """
        Creates relationships between nodes based on their timeline index.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = """
        MATCH (n)
        WHERE n.timeline_index IS NOT NULL
        WITH n
        ORDER BY n.timeline_index ASC

        WITH collect(n) AS nodes

        UNWIND range(0, size(nodes) - 2) AS i
        WITH nodes[i] AS node1, nodes[i + 1] AS node2

        MERGE (node1)-[:NEXT_ON_TIMELINE]->(node2)

        RETURN node1, node2
        """

        result = []
        self.logger.info('Creating timeline relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}')
        return result

    def create_profile_relationships(self):
        """
        Creates 'USES_PROFILE' relationships between extrusions and profiles based on the profile_tokens list.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        // Find extrusions with profile_tokens property and match them to profiles with the same id_token
        MATCH (f:`adsk::fusion::ExtrudeFeature`)
        WHERE f.profile_tokens IS NOT NULL
        UNWIND f.profile_tokens AS profile_token
        MATCH (p:`adsk::fusion::Profile` {id_token: profile_token})
        MERGE (f)-[:USES_PROFILE]->(p)
        RETURN f.id_token AS feature_id, collect(p.id_token) AS profile_ids
        """
        result = []
        self.logger.info('Creating profile/feature relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}')
        return result

    def create_adjacent_face_relationships(self):
        """
        Creates 'ADJACENT' relationships between faces sharing the same edge.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = """
        MATCH (e:`adsk::fusion::BRepEdge`)<-[:CONTAINS]-(f1:`adsk::fusion::BRepFace`), 
              (e)<-[:CONTAINS]-(f2:`adsk::fusion::BRepFace`)
        WHERE id(f1) <> id(f2)
        MERGE (f1)-[:ADJACENT]->(f2)
        MERGE (f2)-[:ADJACENT]->(f1)
        RETURN f1.id_token AS face1_id, f2.id_token AS face2_id
        """
        result = []
        self.logger.info('Creating adjacent face relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}')
        return result

    def create_adjacent_edge_relationships(self):
        """
        Creates 'ADJACENT' relationships between edges sharing the same vertex.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = """
        // Find BRepEdges that share BRepVertices and create ADJACENT relationships between them
        MATCH (v:`adsk::fusion::BRepVertex`)<-[:CONTAINS]-(e1:`adsk::fusion::BRepEdge`), 
            (v)<-[:CONTAINS]-(e2:`adsk::fusion::BRepEdge`)
        WHERE id(e1) <> id(e2)
        MERGE (e1)-[:ADJACENT]->(e2)
        MERGE (e2)-[:ADJACENT]->(e1)
        RETURN e1.id_token AS edge1_id, collect(e2.id_token) AS adjacent_edge_ids
        """
        result = []
        self.logger.info('Creating adjacent edge relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}')
        return result
    
    def create_sketch_relationships(self):
        """
        Creates various relationships between sketch entities.
        - CONNECTED_TO relationships between SketchPoints and SketchEntities.
        - STARTS_AT and ENDS_AT relationships for SketchCurves and SketchPoints.
        - STARTS_AT and ENDS_AT relationships for SketchLines and SketchPoints.
        - CONTAINS relationships between Sketches and Profiles.
        - CONTAINS relationships between Profiles and SketchEntities.

        Returns:
            list: The result values from the query execution.
        """
        queries = {
            'connected_entities': """
            MATCH (sp:`adsk::fusion::SketchPoint`)
            WHERE sp.connectedEntities IS NOT NULL
            UNWIND sp.connectedEntities AS entity_token
            MATCH (se {id_token: entity_token})
            MERGE (sp)-[:CONNECTED_TO]->(se)
            """,
            'sketch_curves': """
            MATCH (sc:`adsk::fusion::SketchCurve`)
            WHERE sc.startPoint IS NOT NULL AND sc.endPoint IS NOT NULL
            MATCH (sp1 {id_token: sc.startPoint})
            MATCH (sp2 {id_token: sc.endPoint})
            MERGE (sc)-[:STARTS_AT]->(sp1)
            MERGE (sc)-[:ENDS_AT]->(sp2)
            """,
            'profile_contains': """
            MATCH (s:`adsk::fusion::Sketch`)-[:CONTAINS]->(p:`adsk::fusion::Profile`)
            WHERE p.profile_curves IS NOT NULL
            UNWIND p.profile_curves AS curve_token
            MATCH (sc {id_token: curve_token})
            MERGE (p)-[:CONTAINS]->(sc)
            """,
            'sketch_lines': """
            MATCH (sc:`adsk::fusion::SketchLine`)
            WHERE sc.startPoint IS NOT NULL AND sc.endPoint IS NOT NULL

            // Ensure that the startPoint and endPoint nodes exist
            WITH sc, sc.startPoint AS startPointToken, sc.endPoint AS endPointToken
            MATCH (sp1 {id_token: startPointToken})
            MATCH (sp2 {id_token: endPointToken})

            // Create relationships
            MERGE (sc)-[:STARTS_AT]->(sp1)
            MERGE (sc)-[:ENDS_AT]->(sp2)

            RETURN sc, sp1, sp2
            """
        }
        result = []
        for name, query in queries.items():
            self.logger.info(f'Creating relationships for {name}')
            try:
                res = self.execute_query(query)
                result.extend(res)
            except Exception as e:
                self.logger.error(f'Exception in {name} relationships: {e}')
        return result


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

    transformer = Neo4jTransformer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        nodes = transformer.create_timeline_relationships()
        for record in nodes:
            print(record)
        transformer.create_face_adjacencies()
    finally:
        transformer.close()

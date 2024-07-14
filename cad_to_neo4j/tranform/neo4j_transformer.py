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
    TimelineTransformer,
    SketchTransformer,
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
        
        # The order matters
        transformation_methods = [
            self.create_profile_relationships, 
            self.component_relationships, # component
            self.brep_relationships, # brep
            self.create_adjacent_face_relationships, # brep
            self.create_adjacent_edge_relationships, # brep
            self.link_sketches_to_planes, # component or timeline
            self.link_construction_planes, # construction
            self.link_feature_to_extents_and_faces, # feature
            self.link_feature_to_axes_bodies_extents, # construction
            self.create_brep_face_relationships # brep
        ]
        
        results = {}
        
        self.logger.info('Running all transformations...')
        
        for method in transformation_methods:
            method_name = method.__name__
            try:
                results[method_name] = method()
                # self.logger.debug(f'Successfully completed {method_name}')
            except Exception as e:
                self.logger.error(f'Exception in {method_name}: {e}\n{traceback.format_exc()}')
        
        return results

    def create_profile_relationships(self):
        """
        Creates 'USES_PROFILE' relationships between feature and profiles based on the profileTokens list.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        // Find features with profileTokens property and match them to profiles with the same entityToken
        MATCH (f:`Feature`)
        WHERE f.profileTokens IS NOT NULL
        UNWIND f.profileTokens AS profile_token
        MATCH (p:`Profile` {entityToken: profile_token})
        MERGE (f)-[:USES_PROFILE]->(p)
        RETURN f.entityToken AS feature_id, collect(p.entityToken) AS profile_ids
        """
        result = []
        self.logger.info('Creating profile/feature relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}\n{traceback.format_exc()}')
        return result

    def component_relationships(self):
        """
        Creates 'CONTAINS' relationships between features, sketches or other timeline entities
        and components containing them.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        // Match existing Entities nodes with a non-null parentComponent
        MATCH (e)
        WHERE ('Sketch' IN labels(e) 
            OR 'Feature' IN labels(e)) 
            AND e.parentComponent IS NOT NULL
        WITH e.parentComponent AS component_token, e
        MATCH (c:Component {entityToken: component_token})
        MERGE (c)-[:CONTAINS]->(e)
        RETURN c, e
        """
        result = []
        self.logger.info('Creating profile/feature relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}\n{traceback.format_exc()}')
        return result
    
    def brep_relationships(self):
        """
        Executes a list of Cypher queries to create relationships between brep entities in the graph database.
        
        Returns:
            list: The result values from the query execution.
        """
        queries = [
            # Create relationships for bodies with entities
            """
            // Match existing Entities nodes with a non-null body property
            MATCH (e)
            WHERE e.body IS NOT NULL
            WITH e.body AS body_entityToken, e
            MATCH (b:BRepBody {entityToken: body_entityToken})
            MERGE (b)-[:CONTAINS]->(e)
            RETURN b, e
            """,
            # Query to connect BRepEdge nodes to BRepFace nodes based on the faces property
            """
            // Match existing BRepEdge nodes with a non-null faces property
            MATCH (e:BRepEdge)
            WHERE e.faces IS NOT NULL
            UNWIND e.faces AS face_entityToken
            MATCH (f:BRepFace {entityToken: face_entityToken})
            MERGE (f)-[:CONTAINS]->(e)
            RETURN e, f
            """,
            # Query to connect BRepFace nodes to BRepEdge nodes based on the edges property
            """
            // Match existing BRepFace nodes with a non-null faces property
            MATCH (f:BRepFace)
            WHERE f.edges IS NOT NULL
            UNWIND f.edges AS edge_entityToken
            MATCH (e:BRepEdge {entityToken: edge_entityToken})
            MERGE (f)-[:CONTAINS]->(e)
            RETURN e, f
            """,
            # Query to create STARTS_WITH and ENDS_WITH relationships for BRepEdge
            """
            // Match existing BRepEdge nodes with startVertex and endVertex properties
            MATCH (e:BRepEdge)
            WHERE e.startVertex IS NOT NULL AND e.endVertex IS NOT NULL
            WITH e, e.startVertex AS start_vertex_id, e.endVertex AS end_vertex_id
            // Match the startVertex node
            MATCH (sv:BRepVertex {entityToken: start_vertex_id})
            MERGE (e)-[:STARTS_WITH]->(sv)
            // Use WITH to separate the MATCH for endVertex
            WITH e, start_vertex_id, end_vertex_id
            // Match the endVertex node
            MATCH (ev:BRepVertex {entityToken: end_vertex_id})
            MERGE (e)-[:ENDS_WITH]->(ev)
            RETURN e
            """,
        ]

        results = []
        self.logger.info('Executing BRep queries')
        for query in queries:
            try:
                result = self.execute_query(query)
                results.append(result)
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        
        return results

    def create_brep_face_relationships(self):
        """
        Creates relationships between BRepEdge nodes and their vertices.

        This method creates 'BOUNDED_BY' relationships between BRepEdge nodes and their start and end vertices.
        The 'BOUNDED_BY' relationship will have a type property indicating whether it is a 'START_WITH' or 'ENDS_WITH' relationship.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            """
            MATCH (feature:Feature)
            WHERE feature.startFaces IS NOT NULL
            UNWIND feature.startFaces AS face_entityToken
            MERGE (face:BRepFace {entityToken: face_entityToken})
            MERGE (feature)-[:BOUNDED_BY {type: 'startFaces'}]->(face)
            """,
            """
            MATCH (feature:Feature)
            WHERE feature.endFaces IS NOT NULL
            UNWIND feature.endFaces AS face_entityToken
            MERGE (face:BRepFace {entityToken: face_entityToken})
            MERGE (feature)-[:BOUNDED_BY {type: 'endFaces'}]->(face)
            """,
            """
            MATCH (feature:Feature)
            WHERE feature.sideFaces IS NOT NULL
            UNWIND feature.sideFaces AS face_entityToken
            MERGE (face:BRepFace {entityToken: face_entityToken})
            MERGE (feature)-[:BOUNDED_BY {type: 'sideFaces'}]->(face)
            """,
            """
            MATCH (f:BRepFace)
            WHERE f.edges IS NOT NULL
            UNWIND f.edges AS edge_entityToken
            MERGE (e:BRepEdge {entityToken: edge_entityToken})
            MERGE (f)-[:BOUNDED_BY]->(e)
            """,
            """
            MATCH (f:BRepFace)
            WHERE NOT (f)-[:BOUNDED_BY]->()
            WITH f
            OPTIONAL MATCH (e:BRepEdge)-[:SURROUNDED_BY]->(f)
            OPTIONAL MATCH (sv:BRepVertex)<-[:STARTS_WITH]-(e)
            OPTIONAL MATCH (ev:BRepVertex)<-[:ENDS_WITH]-(e)
            WITH f, collect(e) AS edges, collect(sv) AS start_vertices, collect(ev) AS end_vertices
            UNWIND edges + start_vertices + end_vertices AS entity
            WITH f, entity WHERE entity IS NOT NULL
            MERGE (f)-[:BOUNDED_BY]->(entity)
            """
        ]
        results = []
        self.logger.info('Creating BRep face relationships')
        for query in queries:
            try:
                result = self.execute_query(query)
                results.extend(result)
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results
    
    def create_adjacent_face_relationships(self):
        """
        Creates 'ADJACENT' relationships between faces sharing the same edge.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        MATCH (e:`BRepEdge`)<-[:CONTAINS]-(f1:`BRepFace`), 
              (e)<-[:CONTAINS]-(f2:`BRepFace`)
        WHERE id(f1) <> id(f2)
        MERGE (f1)-[:ADJACENT]->(f2)
        MERGE (f2)-[:ADJACENT]->(f1)
        RETURN f1.entityToken AS face1_id, f2.entityToken AS face2_id
        """
        result = []
        self.logger.info('Creating adjacent face relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}\n{traceback.format_exc()}')
        return result

    def create_adjacent_edge_relationships(self):
        """
        Creates 'ADJACENT' relationships between edges sharing the same vertex.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        // Find BRepEdges that share BRepVertices and create ADJACENT relationships between them
        MATCH (v:`BRepVertex`)<-[:CONTAINS]-(e1:`BRepEdge`), 
            (v)<-[:CONTAINS]-(e2:`BRepEdge`)
        WHERE id(e1) <> id(e2)
        MERGE (e1)-[:ADJACENT]->(e2)
        MERGE (e2)-[:ADJACENT]->(e1)
        RETURN e1.entityToken AS edge1_id, collect(e2.entityToken) AS adjacent_edge_ids
        """
        result = []
        self.logger.info('Creating adjacent edge relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}\n{traceback.format_exc()}')
        return result
    
    def link_sketches_to_planes(self):
        """
        Creates 'BUILT_ON' relationships between sketches and their reference planes or faces.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        MATCH (s:`Sketch`)
        WHERE s.reference_plane_entity_token IS NOT NULL
        MATCH (p {entityToken: s.reference_plane_entity_token})
        MERGE (s)-[:BUILT_ON]->(p)
        RETURN s.entityToken AS sketch_id, p.entityToken AS plane_id, labels(p) AS plane_labels
        """
        
        result = []
        self.logger.info('Creating sketch to plane/face relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception in linking sketches to planes: {e}\n{traceback.format_exc()}')
        return result

    def link_construction_planes(self):
        """
        Creates relationships between construction planes and their defining entities.

        Returns:
            list: The result values from the query execution.
        """
        cypher_queries = {
            'parent': """
                // Match existing ConstructionEntities nodes with a non-null parentComponent
                MATCH (se)
                WHERE ('ConstructionPlane' IN labels(se) 
                    OR 'ConstructionAxis' IN labels(se) 
                    OR 'ConstructionPoint' IN labels(se)) 
                    AND se.parent IS NOT NULL 

                // Match existing Component node where entityToken matches parent of ConstructionEntities
                MATCH (s:Component {entityToken: se.parent})

                // Create the relationship from Componenet to ConstructionEntities
                MERGE (s)-[:CONTAINS]->(se)
            """,
            'at_angle': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'AtAngle'})
                MATCH (linearEntity {entityToken: cp.linear_entity}), (planarEntity {entityToken: cp.planar_entity})
                MERGE (cp)-[:DEFINED_BY]->(linearEntity)
                MERGE (cp)-[:DEFINED_BY]->(planarEntity)
                RETURN cp.entityToken AS plane_id, linearEntity.entityToken AS linear_entity_id, planarEntity.entityToken AS planar_entity_id
            """,
            'by_plane': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'ByPlane'})
                MATCH (plane {entityToken: cp.plane})
                MERGE (cp)-[:DEFINED_BY]->(plane)
                RETURN cp.entityToken AS plane_id, plane.entityToken AS plane_entity_id
            """,
            'distance_on_path': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'DistanceOnPath'})
                MATCH (pathEntity {entityToken: cp.path_entity})
                MERGE (cp)-[:DEFINED_BY]->(pathEntity)
                RETURN cp.entityToken AS plane_id, pathEntity.entityToken AS path_entity_id
            """,
            'midplane': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'Midplane'})
                MATCH (planarEntityOne {entityToken: cp.planar_entityOne}), (planarEntityTwo {entityToken: cp.planar_entityTwo})
                MERGE (cp)-[:DEFINED_BY]->(planarEntityOne)
                MERGE (cp)-[:DEFINED_BY]->(planarEntityTwo)
                RETURN cp.entityToken AS plane_id, planarEntityOne.entityToken AS planar_entityOne_id, planarEntityTwo.entityToken AS planar_entityTwo_id
            """,
            'offset': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'Offset'})
                MATCH (planarEntity {entityToken: cp.planar_entity})
                MERGE (cp)-[:DEFINED_BY]->(planarEntity)
                RETURN cp.entityToken AS plane_id, planarEntity.entityToken AS planar_entity_id
            """,
            'tangent_at_point': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'TangentAtPoint'})
                MATCH (tangentFace {entityToken: cp.tangent_face}), (pointEntity {entityToken: cp.point_entity})
                MERGE (cp)-[:DEFINED_BY]->(tangentFace)
                MERGE (cp)-[:DEFINED_BY]->(pointEntity)
                RETURN cp.entityToken AS plane_id, tangentFace.entityToken AS tangent_face_id, pointEntity.entityToken AS point_entity_id
            """,
            'tangent': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'Tangent'})
                MATCH (tangentFace {entityToken: cp.tangent_face}), (planarEntity {entityToken: cp.planar_entity})
                MERGE (cp)-[:DEFINED_BY]->(tangentFace)
                MERGE (cp)-[:DEFINED_BY]->(planarEntity)
                RETURN cp.entityToken AS plane_id, tangentFace.entityToken AS tangent_face_id, planarEntity.entityToken AS planar_entity_id
            """,
            'three_points': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'ThreePoints'})
                MATCH (pointEntityOne {entityToken: cp.point_entityOne}), (pointEntityTwo {entityToken: cp.point_entityTwo}), (pointEntityThree {entityToken: cp.point_entity_three})
                MERGE (cp)-[:DEFINED_BY]->(pointEntityOne)
                MERGE (cp)-[:DEFINED_BY]->(pointEntityTwo)
                MERGE (cp)-[:DEFINED_BY]->(pointEntityThree)
                RETURN cp.entityToken AS plane_id, pointEntityOne.entityToken AS point_entityOne_id, pointEntityTwo.entityToken AS point_entityTwo_id, pointEntityThree.entityToken AS point_entity_three_id
            """,
            'two_edges': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'TwoEdges'})
                MATCH (linearEntityOne {entityToken: cp.linear_entityOne}), (linearEntityTwo {entityToken: cp.linear_entityTwo})
                MERGE (cp)-[:DEFINED_BY]->(linearEntityOne)
                MERGE (cp)-[:DEFINED_BY]->(linearEntityTwo)
                RETURN cp.entityToken AS plane_id, linearEntityOne.entityToken AS linear_entityOne_id, linearEntityTwo.entityToken AS linear_entityTwo_id
            """
        }

        result = []
        self.logger.info('Creating relationships for construction planes')
        for definition_type, query in cypher_queries.items():
            try:
                self.logger.info(f'Processing {definition_type} definition type')
                res = self.execute_query(query)
                result.extend(res)
            except Exception as e:
                self.logger.error(f'Exception in linking {definition_type} construction planes: {e}\n{traceback.format_exc()}')
        return result
    
    def link_feature_to_extents_and_faces(self):
        """
        Links features to their extents and faces based on various properties.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        MATCH (f)
        WHERE f.extentOne IS NOT NULL OR f.extentTwo IS NOT NULL
        OPTIONAL MATCH (e1 {entityToken: f.extentOne_object_id})
        OPTIONAL MATCH (e2 {entityToken: f.extentTwo_object_id})
        
        // Create relationships to extents
        FOREACH (ignore IN CASE WHEN f.extentOne_object_id IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_extentOne]->(e1)
        )
        FOREACH (ignore IN CASE WHEN f.extentTwo_object_id IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_extentTwo]->(e2)
        )
        
        // Link to faces
        WITH f
        OPTIONAL MATCH (sf {entityToken: f.startFaces})
        OPTIONAL MATCH (ef {entityToken: f.endFaces})
        OPTIONAL MATCH (sif {entityToken: f.sideFaces})
        
        // Create relationships to faces
        FOREACH (ignore IN CASE WHEN f.startFaces IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_START_FACE]->(sf)
        )
        FOREACH (ignore IN CASE WHEN f.endFaces IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_END_FACE]->(ef)
        )
        FOREACH (ignore IN CASE WHEN f.sideFaces IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_SIDE_FACE]->(sif)
        )
        
        RETURN f.entityToken AS feature_id, 
               f.extentOne_object_id AS extentOne_id, 
               f.extentTwo_object_id AS extentTwo_id,
               f.startFaces AS startFaces,
               f.endFaces AS endFaces,
               f.sideFaces AS sideFaces
        """
        
        result = []
        self.logger.info('Linking features to extents and faces')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception in linking features to extents and faces: {e}')
        return result

    def link_feature_to_axes_bodies_extents(self):
        """
        Links features to their axes, participant bodies, and extents based on various properties.

        Returns:
            list: The result values from the query execution.
        """
        queries = {
            "axis_relationships": r"""
            MATCH (f)
            WHERE f.axisToken IS NOT NULL
            OPTIONAL MATCH (a {entityToken: f.axisToken})
            FOREACH (ignore IN CASE WHEN f.axisToken IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_AXIS]->(a)
            )
            RETURN f.entityToken AS feature_id, f.axisToken AS axis_id
            """,
            "participant_body_relationships": r"""
            MATCH (f)
            WHERE f.participantBodies IS NOT NULL
            UNWIND f.participantBodies AS body_token
            OPTIONAL MATCH (b {entityToken: body_token})
            WITH f, b, body_token WHERE b IS NOT NULL
            FOREACH (ignore IN CASE WHEN body_token IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_PARTICIPANT_BODY]->(b)
            )
            RETURN f.entityToken AS feature_id, collect(b.entityToken) AS participant_body_ids
            """,
            "extentOne_relationships": r"""
            MATCH (f)
            WHERE f.extentOne_object_id IS NOT NULL
            OPTIONAL MATCH (e1 {entityToken: f.extentOne_object_id})
            FOREACH (ignore IN CASE WHEN f.extentOne_object_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_extentOne]->(e1)
            )
            RETURN f.entityToken AS feature_id, f.extentOne_object_id AS extentOne_id
            """,
            "extentTwo_relationships": r"""
            MATCH (f)
            WHERE f.extentTwo_object_id IS NOT NULL
            OPTIONAL MATCH (e2 {entityToken: f.extentTwo_object_id})
            FOREACH (ignore IN CASE WHEN f.extentTwo_object_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_extentTwo]->(e2)
            )
            RETURN f.entityToken AS feature_id, f.extentTwo_object_id AS extentTwo_id
            """
        }

        results = []
        self.logger.info('Linking features to axes, participant bodies, and extents')
        for name, query in queries.items():
            try:
                result = self.execute_query(query)
                results.extend(result)
                self.logger.info(f'Successfully completed {name}')
            except Exception as e:
                self.logger.error(f'Exception in {name}: {e}\n{traceback.format_exc()}')

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

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
        
        transformation_methods = [
            self.create_timeline_relationships,
            self.create_profile_relationships,
            self.create_adjacent_face_relationships,
            self.create_adjacent_edge_relationships,
            self.create_sketch_relationships,
            self.link_sketches_to_planes,
            self.link_sketch_entities_to_dimensions,
            self.link_construction_planes,
            self.link_feature_to_extents_and_faces,
            self.link_feature_to_axes_bodies_extents,
        ]
        
        results = {}
        
        self.logger.info('Running all transformations...')
        
        for method in transformation_methods:
            method_name = method.__name__
            try:
                results[method_name] = method()
                self.logger.info(f'Successfully completed {method_name}')
            except Exception as e:
                self.logger.error(f'Exception in {method_name}: {e}')
        
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
        MATCH (f:`ExtrudeFeature`)
        WHERE f.profile_tokens IS NOT NULL
        UNWIND f.profile_tokens AS profile_token
        MATCH (p:`Profile` {id_token: profile_token})
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
        cypher_query = r"""
        MATCH (e:`BRepEdge`)<-[:CONTAINS]-(f1:`BRepFace`), 
              (e)<-[:CONTAINS]-(f2:`BRepFace`)
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
        cypher_query = r"""
        // Find BRepEdges that share BRepVertices and create ADJACENT relationships between them
        MATCH (v:`BRepVertex`)<-[:CONTAINS]-(e1:`BRepEdge`), 
            (v)<-[:CONTAINS]-(e2:`BRepEdge`)
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
            'connected_entities': r"""
            MATCH (sp:`SketchPoint`)
            WHERE sp.connectedEntities IS NOT NULL
            UNWIND sp.connectedEntities AS entity_token
            MATCH (se {id_token: entity_token})
            MERGE (sp)-[:CONNECTED_TO]->(se)
            """,
            'sketch_curves': r"""
            MATCH (sc:`SketchCurve`)
            WHERE sc.startPoint IS NOT NULL AND sc.endPoint IS NOT NULL
            MATCH (sp1 {id_token: sc.startPoint})
            MATCH (sp2 {id_token: sc.endPoint})
            MERGE (sc)-[:STARTS_AT]->(sp1)
            MERGE (sc)-[:ENDS_AT]->(sp2)
            """,
            'profile_contains': r"""
            MATCH (s:`Sketch`)-[:CONTAINS]->(p:`Profile`)
            WHERE p.profile_curves IS NOT NULL
            UNWIND p.profile_curves AS curve_token
            MATCH (sc {id_token: curve_token})
            MERGE (p)-[:CONTAINS]->(sc)
            """,
            'sketch_lines': r"""
            MATCH (sc:`SketchLine`)
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
    
    def link_sketches_to_planes(self):
        """
        Creates 'BUILT_ON' relationships between sketches and their reference planes or faces.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        MATCH (s:`Sketch`)
        WHERE s.reference_plane_entity_token IS NOT NULL
        MATCH (p {id_token: s.reference_plane_entity_token})
        MERGE (s)-[:BUILT_ON]->(p)
        RETURN s.id_token AS sketch_id, p.id_token AS plane_id, labels(p) AS plane_labels
        """
        
        result = []
        self.logger.info('Creating sketch to plane/face relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception in linking sketches to planes: {e}')
        return result
    
    def link_sketch_entities_to_dimensions(self):
        """
        Creates 'LINKED_TO_DIMENSION' relationships between sketch entities and their corresponding dimensions.

        This function connects any node with a sketchDimensions property to all the SketchDimension nodes
        that share the same id_token as the ones in the list under the sketchDimensions property.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        MATCH (n)
        WHERE n.sketchDimensions IS NOT NULL AND size(n.sketchDimensions) > 0
        WITH n, n.sketchDimensions AS dimension_tokens
        UNWIND dimension_tokens AS dimension_token
        MATCH (d) WHERE d.id_token = dimension_token
        MERGE (n)-[:LINKED_TO_DIMENSION]->(d)
        RETURN n.id_token AS entity_id, collect(d.id_token) AS dimension_ids, labels(n) AS entity_labels
        """
        
        result = []
        self.logger.info('Creating relationships between sketch entities and their dimensions')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception in linking sketch entities to dimensions: {e}')
        return result

    def link_construction_planes(self):
        """
        Creates relationships between construction planes and their defining entities.

        Returns:
            list: The result values from the query execution.
        """
        cypher_queries = {
            'at_angle': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'AtAngle'})
                MATCH (linearEntity {id_token: cp.linear_entity}), (planarEntity {id_token: cp.planar_entity})
                MERGE (cp)-[:DEFINED_BY]->(linearEntity)
                MERGE (cp)-[:DEFINED_BY]->(planarEntity)
                RETURN cp.id_token AS plane_id, linearEntity.id_token AS linear_entity_id, planarEntity.id_token AS planar_entity_id
            """,
            'by_plane': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'ByPlane'})
                MATCH (plane {id_token: cp.plane})
                MERGE (cp)-[:DEFINED_BY]->(plane)
                RETURN cp.id_token AS plane_id, plane.id_token AS plane_entity_id
            """,
            'distance_on_path': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'DistanceOnPath'})
                MATCH (pathEntity {id_token: cp.path_entity})
                MERGE (cp)-[:DEFINED_BY]->(pathEntity)
                RETURN cp.id_token AS plane_id, pathEntity.id_token AS path_entity_id
            """,
            'midplane': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'Midplane'})
                MATCH (planarEntityOne {id_token: cp.planar_entity_one}), (planarEntityTwo {id_token: cp.planar_entity_two})
                MERGE (cp)-[:DEFINED_BY]->(planarEntityOne)
                MERGE (cp)-[:DEFINED_BY]->(planarEntityTwo)
                RETURN cp.id_token AS plane_id, planarEntityOne.id_token AS planar_entity_one_id, planarEntityTwo.id_token AS planar_entity_two_id
            """,
            'offset': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'Offset'})
                MATCH (planarEntity {id_token: cp.planar_entity})
                MERGE (cp)-[:DEFINED_BY]->(planarEntity)
                RETURN cp.id_token AS plane_id, planarEntity.id_token AS planar_entity_id
            """,
            'tangent_at_point': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'TangentAtPoint'})
                MATCH (tangentFace {id_token: cp.tangent_face}), (pointEntity {id_token: cp.point_entity})
                MERGE (cp)-[:DEFINED_BY]->(tangentFace)
                MERGE (cp)-[:DEFINED_BY]->(pointEntity)
                RETURN cp.id_token AS plane_id, tangentFace.id_token AS tangent_face_id, pointEntity.id_token AS point_entity_id
            """,
            'tangent': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'Tangent'})
                MATCH (tangentFace {id_token: cp.tangent_face}), (planarEntity {id_token: cp.planar_entity})
                MERGE (cp)-[:DEFINED_BY]->(tangentFace)
                MERGE (cp)-[:DEFINED_BY]->(planarEntity)
                RETURN cp.id_token AS plane_id, tangentFace.id_token AS tangent_face_id, planarEntity.id_token AS planar_entity_id
            """,
            'three_points': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'ThreePoints'})
                MATCH (pointEntityOne {id_token: cp.point_entity_one}), (pointEntityTwo {id_token: cp.point_entity_two}), (pointEntityThree {id_token: cp.point_entity_three})
                MERGE (cp)-[:DEFINED_BY]->(pointEntityOne)
                MERGE (cp)-[:DEFINED_BY]->(pointEntityTwo)
                MERGE (cp)-[:DEFINED_BY]->(pointEntityThree)
                RETURN cp.id_token AS plane_id, pointEntityOne.id_token AS point_entity_one_id, pointEntityTwo.id_token AS point_entity_two_id, pointEntityThree.id_token AS point_entity_three_id
            """,
            'two_edges': """
                MATCH (cp:`ConstructionPlane` {definition_type: 'TwoEdges'})
                MATCH (linearEntityOne {id_token: cp.linear_entity_one}), (linearEntityTwo {id_token: cp.linear_entity_two})
                MERGE (cp)-[:DEFINED_BY]->(linearEntityOne)
                MERGE (cp)-[:DEFINED_BY]->(linearEntityTwo)
                RETURN cp.id_token AS plane_id, linearEntityOne.id_token AS linear_entity_one_id, linearEntityTwo.id_token AS linear_entity_two_id
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
                self.logger.error(f'Exception in linking {definition_type} construction planes: {e}')
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
        OPTIONAL MATCH (e1 {id_token: f.extentOne_object_id})
        OPTIONAL MATCH (e2 {id_token: f.extentTwo_object_id})
        
        // Create relationships to extents
        FOREACH (ignore IN CASE WHEN f.extentOne_object_id IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_EXTENT_ONE]->(e1)
        )
        FOREACH (ignore IN CASE WHEN f.extentTwo_object_id IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_EXTENT_TWO]->(e2)
        )
        
        // Link to faces
        WITH f
        OPTIONAL MATCH (sf {id_token: f.start_faces})
        OPTIONAL MATCH (ef {id_token: f.end_faces})
        OPTIONAL MATCH (sif {id_token: f.side_faces})
        
        // Create relationships to faces
        FOREACH (ignore IN CASE WHEN f.start_faces IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_START_FACE]->(sf)
        )
        FOREACH (ignore IN CASE WHEN f.end_faces IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_END_FACE]->(ef)
        )
        FOREACH (ignore IN CASE WHEN f.side_faces IS NOT NULL THEN [1] ELSE [] END |
            MERGE (f)-[:HAS_SIDE_FACE]->(sif)
        )
        
        RETURN f.id_token AS feature_id, 
               f.extentOne_object_id AS extent_one_id, 
               f.extentTwo_object_id AS extent_two_id,
               f.start_faces AS start_faces,
               f.end_faces AS end_faces,
               f.side_faces AS side_faces
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
            WHERE f.axis_token IS NOT NULL
            OPTIONAL MATCH (a {id_token: f.axis_token})
            FOREACH (ignore IN CASE WHEN f.axis_token IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_AXIS]->(a)
            )
            RETURN f.id_token AS feature_id, f.axis_token AS axis_id
            """,
            "participant_body_relationships": r"""
            MATCH (f)
            WHERE f.participant_bodies IS NOT NULL
            UNWIND f.participant_bodies AS body_token
            OPTIONAL MATCH (b {id_token: body_token})
            WITH f, b, body_token WHERE b IS NOT NULL
            FOREACH (ignore IN CASE WHEN body_token IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_PARTICIPANT_BODY]->(b)
            )
            RETURN f.id_token AS feature_id, collect(b.id_token) AS participant_body_ids
            """,
            "extent_one_relationships": r"""
            MATCH (f)
            WHERE f.extentOne_object_id IS NOT NULL
            OPTIONAL MATCH (e1 {id_token: f.extentOne_object_id})
            FOREACH (ignore IN CASE WHEN f.extentOne_object_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_EXTENT_ONE]->(e1)
            )
            RETURN f.id_token AS feature_id, f.extentOne_object_id AS extent_one_id
            """,
            "extent_two_relationships": r"""
            MATCH (f)
            WHERE f.extentTwo_object_id IS NOT NULL
            OPTIONAL MATCH (e2 {id_token: f.extentTwo_object_id})
            FOREACH (ignore IN CASE WHEN f.extentTwo_object_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_EXTENT_TWO]->(e2)
            )
            RETURN f.id_token AS feature_id, f.extentTwo_object_id AS extent_two_id
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
                self.logger.error(f'Exception in {name}: {e}')

        return results
    
    def link_sketch_dimensions(self):
        """
        Creates relationships between entities and their sketch dimensions based on various properties.

        Returns:
            dict: A dictionary containing the results of all transformations.
        """
        queries = [
            """
            MATCH (dim:SketchDimension)
            WHERE dim.point IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.point
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.line IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.line
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.line_one IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.line_one
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.line_two IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.line_two
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.circle_one IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.circle_one
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.circle_two IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.circle_two
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.entity IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.entity
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.entity_one IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.entity_one
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.entity_two IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.entity_two
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.planar_surface IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.planar_surface
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.surface IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.surface
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.ellipse IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.ellipse
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.offset_constraint IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.offset_constraint
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """,
            """
            MATCH (dim:SketchDimension)
            WHERE dim.circle_or_arc IS NOT NULL
            MATCH (e) WHERE e.id_token = dim.circle_or_arc
            MERGE (e)-[:HAS_DIMENSION]->(dim)
            """
        ]

        results = []
        for query in queries:
            self.logger.info(f'Executing query: {query}')
            try:
                result = self.execute_query(query)
                results.extend(result)
            except Exception as e:
                self.logger.error(f'Exception in executing query: {e}')

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

    transformer = Neo4jTransformer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        nodes = transformer.create_timeline_relationships()
        for record in nodes:
            print(record)
        transformer.create_face_adjacencies()
    finally:
        transformer.close()

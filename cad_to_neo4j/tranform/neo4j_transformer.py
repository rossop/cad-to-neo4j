"""
Neo4j Transformer Module

This module provides functions to transform CAD data in a Neo4j graph database.

Classes:
    - Neo4jTransformer: A class to handle transformations in a Neo4j graph database.
"""

from ..utils.neo4j_utils import Neo4jTransactionManager
import logging
import traceback 

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
        
        # The order matters
        transformation_methods = [
            self.create_timeline_relationships, # REVIEWED
            self.create_sketch_relationships,
            self.create_profile_relationships,
            self.component_relationships,
            self.brep_relationships,
            self.create_adjacent_face_relationships,
            self.create_adjacent_edge_relationships,
            self.link_sketches_to_planes,
            self.create_sketch_dimensions_relationships,
            self.link_construction_planes,
            self.link_feature_to_extents_and_faces,
            self.link_feature_to_axes_bodies_extents,
            self.create_sketch_axis_and_origin_for_all_sketches,
            self.create_sketch_geometric_constraints,
            self.create_brep_face_relationships
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
            self.logger.error(f'Exception: {e}\n{traceback.format_exc()}')
        return result

    def create_profile_relationships(self):
        """
        Creates 'USES_PROFILE' relationships between feature and profiles based on the profileTokens list.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = r"""
        // Find features with profileTokens property and match them to profiles with the same id_token
        MATCH (f:`Feature`)
        WHERE f.profileTokens IS NOT NULL
        UNWIND f.profileTokens AS profile_token
        MATCH (p:`Profile` {id_token: profile_token})
        MERGE (f)-[:USES_PROFILE]->(p)
        RETURN f.id_token AS feature_id, collect(p.id_token) AS profile_ids
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
        MATCH (c:Component {id_token: component_token})
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
            WITH e.body AS body_id_token, e
            MATCH (b:BRepBody {id_token: body_id_token})
            MERGE (b)-[:CONTAINS]->(e)
            RETURN b, e
            """,
            # Query to connect BRepEdge nodes to BRepFace nodes based on the faces property
            """
            // Match existing BRepEdge nodes with a non-null faces property
            MATCH (e:BRepEdge)
            WHERE e.faces IS NOT NULL
            UNWIND e.faces AS face_id_token
            MATCH (f:BRepFace {id_token: face_id_token})
            MERGE (f)-[:CONTAINS]->(e)
            RETURN e, f
            """,
            # Query to connect BRepFace nodes to BRepEdge nodes based on the edges property
            """
            // Match existing BRepFace nodes with a non-null faces property
            MATCH (f:BRepFace)
            WHERE f.edges IS NOT NULL
            UNWIND f.edges AS edge_id_token
            MATCH (e:BRepEdge {id_token: edge_id_token})
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
            MATCH (sv:BRepVertex {id_token: start_vertex_id})
            MERGE (e)-[:STARTS_WITH]->(sv)
            // Use WITH to separate the MATCH for endVertex
            WITH e, start_vertex_id, end_vertex_id
            // Match the endVertex node
            MATCH (ev:BRepVertex {id_token: end_vertex_id})
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
            UNWIND feature.startFaces AS face_id_token
            MERGE (face:BRepFace {id_token: face_id_token})
            MERGE (feature)-[:BOUNDED_BY {type: 'startFaces'}]->(face)
            """,
            """
            MATCH (feature:Feature)
            WHERE feature.endFaces IS NOT NULL
            UNWIND feature.endFaces AS face_id_token
            MERGE (face:BRepFace {id_token: face_id_token})
            MERGE (feature)-[:BOUNDED_BY {type: 'endFaces'}]->(face)
            """,
            """
            MATCH (feature:Feature)
            WHERE feature.sideFaces IS NOT NULL
            UNWIND feature.sideFaces AS face_id_token
            MERGE (face:BRepFace {id_token: face_id_token})
            MERGE (feature)-[:BOUNDED_BY {type: 'sideFaces'}]->(face)
            """,
            """
            MATCH (f:BRepFace)
            WHERE f.edges IS NOT NULL
            UNWIND f.edges AS edge_id_token
            MERGE (e:BRepEdge {id_token: edge_id_token})
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
        RETURN f1.id_token AS face1_id, f2.id_token AS face2_id
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
        RETURN e1.id_token AS edge1_id, collect(e2.id_token) AS adjacent_edge_ids
        """
        result = []
        self.logger.info('Creating adjacent edge relationships')
        try:
            result = self.execute_query(cypher_query)
        except Exception as e:
            self.logger.error(f'Exception: {e}\n{traceback.format_exc()}')
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
            # TODO some dimension and constraints relationships depend on 
            #   CONTAONS being already defined, resolve it.
            # TODO remove the parentSketch relationship 
            'sketch associated entities': r"""
            // Match existing SketchEntity nodes with a non-null parentSketch
            MATCH (se)
            WHERE ('SketchEntity' IN labels(se) 
                OR 'SketchDimension' IN labels(se) 
                OR 'GeometricConstraint' IN labels(se) 
                OR 'Profile' IN labels(se)) 
                AND se.parentSketch IS NOT NULL 

            // Match existing Sketch node where id_token matches parentSketch of SketchEntity
            MATCH (s:Sketch {id_token: se.parentSketch})

            // Create the relationship from Sketch to SketchEntity
            MERGE (s)-[:CONTAINS]->(se)
            """,
            'connected_entities': r"""
            MATCH (sp:`SketchPoint`)
            WHERE sp.connectedEntities IS NOT NULL
            UNWIND sp.connectedEntities AS entity_token
            MATCH (se {id_token: entity_token})
            WHERE NOT 'SketchCurve' IN labels(se)
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
            """,
            'circle_center': r"""
            MATCH (circle)
            WHERE circle.centerPoint IS NOT NULL
            MATCH (center {id_token: circle.centerPoint})
            MERGE (circle)-[:CENTERED_ON]->(center)
            REMOVE circle.centerPoint
            RETURN circle, center
            """,
            'projection': r"""
            MATCH (se:SketchEntity)
            WHERE se.referencedEntity IS NOT NULL
            MATCH (re:SketchEntity)
            WHERE re.id_token = se.referencedEntity
            MERGE (re)-[:PROJECTED_TO]->(se)
            RETURN se,re
            """,
        }
        result = []
        for name, query in queries.items():
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
            self.logger.error(f'Exception in linking sketches to planes: {e}\n{traceback.format_exc()}')
        return result
    
    def create_sketch_dimensions_relationships(self):
        """
        Creates 'DIMENSIONED' relationships between sketch entities and their corresponding dimensions.

        This function connects any node with a sketchDimensions property to all the SketchDimension nodes
        that share the same id_token as the ones in the list under the sketchDimensions property.

        Returns:
            list: The result values from the query execution.
        """
        cypher_queries = [
            """
            MATCH (d)
            WHERE ('SketchDimension' IN labels(d) OR 'SketchLinearDimension' IN labels(d)) 
                AND d.entity_one IS NOT NULL 
                AND d.entity_two IS NOT NULL
            MATCH (a {id_token: d.entity_one})
            MATCH (b {id_token: d.entity_two})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.entity_one, d.entity_two
            """,
            """
            MATCH (d)
            WHERE (d:SketchAngularDimension) 
                AND d.line_one IS NOT NULL 
                AND d.line_two IS NOT NULL
            MATCH (a {id_token: d.line_one})
            MATCH (b {id_token: d.line_two})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.line_one, d.line_two
            """,   
            """
            MATCH (d)
            WHERE (d:SketchConcentricCircleDimension) 
                AND d.circle_one IS NOT NULL 
                AND d.circle_two IS NOT NULL
            MATCH (a {id_token: d.circle_one})
            MATCH (b {id_token: d.circle_two})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.circle_one, d.circle_two
            """,   
            """
            MATCH (d)
            WHERE ('SketchDiameterDimension' IN labels(d) OR 'SketchRadialDimension' IN labels(d))
                AND d.entity IS NOT NULL 
            MATCH (a {id_token: d.entity})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(a)
            REMOVE d.entity
            """,
            """
            MATCH (d)
            WHERE (d:SketchDistanceBetweenLineAndPlanarSurfaceDimension) 
                AND d.line IS NOT NULL 
                AND d.planar_surface IS NOT NULL
            MATCH (a {id_token: d.line})
            MATCH (b {id_token: d.planar_surface})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.line, d.planar_surface
            """,   
            """
            MATCH (d)
            WHERE (d:SketchDistanceBetweenPointAndSurfaceDimension) 
                AND d.point IS NOT NULL 
                AND d.surface IS NOT NULL
            MATCH (a {id_token: d.point})
            MATCH (b {id_token: d.surface})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.point, d.surface
            """,   
            """
            MATCH (d)
            WHERE (d:SketchLinearDiameterDimension) 
                AND d.line IS NOT NULL 
                AND d.entity_two IS NOT NULL
            MATCH (a {id_token: d.line})
            MATCH (b {id_token: d.entity_two})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.line, d.entity_two
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetCurvesDimension) 
                AND d.offset_constraint IS NOT NULL 
            MATCH (c {id_token: d.offset_constraint})
            MERGE (c)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.offset_constraint
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetCurvesDimension) 
                AND d.offset_constraint IS NOT NULL 
            MATCH (c {id_token: d.offset_constraint})
            MERGE (c)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.offset_constraint
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetDimension) 
                AND d.line IS NOT NULL 
                AND d.entity_two IS NOT NULL 
            MATCH (a {id_token: d.line})
            MATCH (c {id_token: d.entity_two})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.line, d.entity_two
            """,
            #  Redundancy check for Circle entities dimensions
            """
            // Query to create DIMENSIONED relationships using the dimensions property of SketchCircle

            // Unwind dimensions and create DIMENSIONED relationships from dimension to circle
            MATCH (circle:SketchCircle)
            UNWIND circle.dimensions AS dimension_id
            MATCH (dim:SketchDimension {id_token: dimension_id})
            WHERE NOT (dim)-[:DIMENSIONED]->(circle)
            MERGE (dim)-[:DIMENSIONED]->(circle)
            RETURN circle, dim;
            """,
            """
            // Unwind dimensions and create DIMENSIONED relationships from circle to dimension
            MATCH (circle:SketchCircle)
            UNWIND circle.dimensions AS dimension_id
            MATCH (dim:SketchDimension {id_token: dimension_id})
            WHERE NOT (circle)-[:DIMENSIONED]->(dim)
            MERGE (circle)-[:DIMENSIONED]->(dim)
            REMOVE circle.dimensions
            RETURN circle, dim;
            """
        ]
        
        result = []
        self.logger.info('Creating relationships between sketch entities and their dimensions')
        try:
            for query in cypher_queries:
                result.append(self.execute_query(query))
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
            'parent': """
                // Match existing ConstructionEntities nodes with a non-null parentComponent
                MATCH (se)
                WHERE ('ConstructionPlane' IN labels(se) 
                    OR 'ConstructionAxis' IN labels(se) 
                    OR 'ConstructionPoint' IN labels(se)) 
                    AND se.parent IS NOT NULL 

                // Match existing Component node where id_token matches parent of ConstructionEntities
                MATCH (s:Component {id_token: se.parent})

                // Create the relationship from Componenet to ConstructionEntities
                MERGE (s)-[:CONTAINS]->(se)
            """,
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
        OPTIONAL MATCH (sf {id_token: f.startFaces})
        OPTIONAL MATCH (ef {id_token: f.endFaces})
        OPTIONAL MATCH (sif {id_token: f.sideFaces})
        
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
        
        RETURN f.id_token AS feature_id, 
               f.extentOne_object_id AS extent_one_id, 
               f.extentTwo_object_id AS extent_two_id,
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
            WHERE f.axis_token IS NOT NULL
            OPTIONAL MATCH (a {id_token: f.axis_token})
            FOREACH (ignore IN CASE WHEN f.axis_token IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_AXIS]->(a)
            )
            RETURN f.id_token AS feature_id, f.axis_token AS axis_id
            """,
            "participant_body_relationships": r"""
            MATCH (f)
            WHERE f.participantBodies IS NOT NULL
            UNWIND f.participantBodies AS body_token
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
                self.logger.error(f'Exception in {name}: {e}\n{traceback.format_exc()}')

        return results

    def create_sketch_geometric_constraints(self):
        """
        Creates relationships between entities and their geometric constraints based on various properties.

        Returns:
            dict: A dictionary containing the results of all transformations.
        """
        queries = [ 
            # Creates relationships for CircularPatternConstraint entities.
            """
            MATCH (c:CircularPatternConstraint)
            WHERE c.entities IS NOT NULL AND c.created_entities IS NOT NULL AND c.center_point IS NOT NULL
            UNWIND c.entities AS entity_token
            MATCH (se {id_token: entity_token}) // Source Entities
            WITH c, se
            UNWIND c.created_entities AS created_entity_token
            MATCH (te {id_token: created_entity_token}) // Target Entities
            WITH c, se, te
            MATCH (ce {id_token: c.center_point}) // Center Point
            MERGE (se)-[:CONSTRAINED]->(c)
            MERGE (c)-[:CONSTRAINED]->(te)
            MERGE (ce)-[:CONSTRAINED]->(c)
            REMOVE c.entities, c.created_entities, c.center_point
            RETURN c, se, te, ce
            """,
            # Creates relationships for VerticalConstraint entities with yAxis.
            """   
            MATCH (vc:VerticalConstraint)
            WHERE vc.line IS NOT NULL
            UNWIND vc.line AS entity_token
            MATCH (se {id_token: entity_token}) // Source Entities
            MATCH (sa:SketchAxis {name: 'y'}) // Target SketchAxis
            WITH vc, se, sa
            MATCH (vc)<-[:CONTAINS]-(s:Sketch)-[:CONTAINS]->(sa)
            MERGE (se)-[:CONSTRAINED]->(vc)
            MERGE (vc)-[:CONSTRAINED]->(sa)
            REMOVE vc.line
            RETURN vc, se, sa
            """,
            # Creates relationships for HorizontalConstraint entities with xAxis.
            """
            MATCH (hc:HorizontalConstraint)
            WHERE hc.line IS NOT NULL
            UNWIND hc.line AS entity_token
            MATCH (se {id_token: entity_token}) // Source Entities
            MATCH (sa:SketchAxis {name: 'x'}) // Target SketchAxis
            WITH hc, se, sa
            MATCH (hc)<-[:CONTAINS]-(s:Sketch)-[:CONTAINS]->(sa)
            MERGE (se)-[:CONSTRAINED]->(hc)
            MERGE (hc)-[:CONSTRAINED]->(sa)
            // REMOVE hc.line
            RETURN hc, se, sa
            """,
            # Creates relationships for PerpendicularConstraint entities linking line_one and line_two.
            """
            MATCH (pc:PerpendicularConstraint)
            WHERE pc.line_one IS NOT NULL AND pc.line_two IS NOT NULL
            MATCH (source {id_token: pc.line_one}) // Source Entity
            MATCH (target {id_token: pc.line_two}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(pc)
            MERGE (pc)-[:CONSTRAINED]->(target)
            REMOVE pc.line_one, pc.line_two
            RETURN pc, source, target
            """,
            # Creates relationships for CoincidentConstraint entities linking point and entity.
            """
            MATCH (cc:CoincidentConstraint)
            WHERE cc.point IS NOT NULL AND cc.entity IS NOT NULL
            MATCH (source {id_token: cc.point}) // Source Entity
            MATCH (target {id_token: cc.entity}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(cc)
            MERGE (cc)-[:CONSTRAINED]->(target)
            REMOVE cc.point, cc.entity
            RETURN cc, source, target
            """,
            # Creates relationships for CollinearConstraint entities linking line_one and line_two.
            """
            MATCH (cc:CollinearConstraint)
            WHERE cc.line_one IS NOT NULL AND cc.line_two IS NOT NULL
            MATCH (source {id_token: cc.line_one}) // Source Entity
            MATCH (target {id_token: cc.line_two}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(cc)
            MERGE (cc)-[:CONSTRAINED]->(target)
            REMOVE cc.line_one, cc.line_two
            RETURN cc, source, target
            """,
            # Creates relationships for EqualConstraint entities linking curve_one and curve_two.
            """
            MATCH (ec:EqualConstraint)
            WHERE ec.curve_one IS NOT NULL AND ec.curve_two IS NOT NULL
            MATCH (source {id_token: ec.curve_one}) // Source Entity
            MATCH (target {id_token: ec.curve_two}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(ec)
            MERGE (ec)-[:CONSTRAINED]->(target)
            REMOVE ec.curve_one, ec.curve_two
            RETURN ec, source, target
            """,
            # Creates relationships for ParallelConstraint entities linking line_one and line_two.
            """
            MATCH (pc:ParallelConstraint)
            WHERE pc.line_one IS NOT NULL AND pc.line_two IS NOT NULL
            MATCH (source {id_token: pc.line_one}) // Source Entity
            MATCH (target {id_token: pc.line_two}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(pc)
            MERGE (pc)-[:CONSTRAINED]->(target)
            REMOVE pc.line_one, pc.line_two
            RETURN pc, source, target
            """,
            # reates relationships for SymmetryConstraint entities linking entity_one, entity_two, and symmetry_line.
            """
            MATCH (sc:SymmetryConstraint)
            WHERE sc.entity_one IS NOT NULL AND sc.entity_two IS NOT NULL AND sc.symmetry_line IS NOT NULL
            MATCH (source {id_token: sc.entity_one}) // Source Entity
            MATCH (target {id_token: sc.entity_two}) // Target Entity
            MATCH (symmetry_line {id_token: sc.symmetry_line}) // Symmetry Line
            MERGE (source)-[:CONSTRAINED]->(sc)
            MERGE (sc)-[:CONSTRAINED]->(target)
            MERGE (symmetry_line)-[:CONSTRAINED]->(sc)
            REMOVE sc.entity_one, sc.entity_two, sc.symmetry_line
            RETURN sc, source, target, symmetry_line
            """,
            # Creates relationships for TangentConstraint entities linking curve_one and curve_two.
            """
            MATCH (tc:TangentConstraint)
            WHERE tc.curve_one IS NOT NULL AND tc.curve_two IS NOT NULL
            MATCH (source {id_token: tc.curve_one}) // Source Entity
            MATCH (target {id_token: tc.curve_two}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(tc)
            MERGE (tc)-[:CONSTRAINED]->(target)
            REMOVE tc.curve_one, tc.curve_two
            RETURN tc, source, target
            """,
        ]
        
        results = []
        for query in queries:
            try:
                result = self.execute_query(query)
                results.extend(result)
            except Exception as e:
                self.logger.error(f'Exception in executing query: {e}')
        
        return results
    
    def create_sketch_axis_and_origin_for_all_sketches(self):
        """
        Matches all existing Sketch nodes, extracts axis and origin information,
        and creates SketchAxis and SketchOrigin nodes with relationships.

        Returns:
            None
        """
        try:
            query = """
            MATCH (sketch:Sketch)
            WITH sketch, sketch.origin AS origin_position, sketch.x_direction AS x_axis_vector, sketch.y_direction AS y_axis_vector, sketch.origin_point AS origin_id_token
            MERGE (origin:SketchEntity {id_token: origin_id_token})
            ON CREATE SET origin.position = origin_position
            ON MATCH SET origin :SketchOrigin
            SET origin :SketchEntity
            MERGE (x_axis:SketchAxis:SketchEntity {name: 'x', vector: x_axis_vector})
            MERGE (y_axis:SketchAxis:SketchEntity {name: 'y', vector: y_axis_vector})
            MERGE (x_axis)-[:STARTS_WITH]->(origin)
            MERGE (y_axis)-[:STARTS_WITH]->(origin)
            MERGE (y_axis)-[:PERPENDICULAR_TO]->(x_axis)
            MERGE (sketch)-[:CONTAINS]->(x_axis)
            MERGE (sketch)-[:CONTAINS]->(y_axis)
            MERGE (sketch)-[:CONTAINS]->(origin)
            """

            self.execute_query(query)
            self.logger.info("Successfully created sketch axis and origin nodes for all sketches")
        except Exception as e:
            self.logger.error(f"Error creating sketch axis and origin nodes for all sketches: {e}\n{traceback.format_exc()}")

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

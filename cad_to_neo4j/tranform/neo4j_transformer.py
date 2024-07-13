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

from .core.strategies import TimelineTransformer

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
            TimelineTransformer(self.logger)
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
            self.create_sketch_relationships, # sketch
            self.create_profile_relationships, 
            self.component_relationships, # component
            self.brep_relationships, # brep
            self.create_adjacent_face_relationships, # brep
            self.create_adjacent_edge_relationships, # brep
            self.link_sketches_to_planes, # component or timeline
            self.create_sketch_dimensions_relationships, # sketch
            self.link_construction_planes, # construction
            self.link_feature_to_extents_and_faces, # feature
            self.link_feature_to_axes_bodies_extents, # construction
            self.create_sketch_axis_and_origin_for_all_sketches, # sketches
            self.create_sketch_geometric_constraints, # sketch
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

            // Match existing Sketch node where entityToken matches parentSketch of SketchEntity
            MATCH (s:Sketch {entityToken: se.parentSketch})

            // Create the relationship from Sketch to SketchEntity
            MERGE (s)-[:CONTAINS]->(se)
            """,
            'connected_entities': r"""
            MATCH (sp:`SketchPoint`)
            WHERE sp.connectedEntities IS NOT NULL
            UNWIND sp.connectedEntities AS entity_token
            MATCH (se {entityToken: entity_token})
            WHERE NOT 'SketchCurve' IN labels(se)
            MERGE (sp)-[:CONNECTED_TO]->(se)
            """,
            'sketch_curves': r"""
            MATCH (sc:`SketchCurve`)
            WHERE sc.startPoint IS NOT NULL AND sc.endPoint IS NOT NULL
            MATCH (sp1 {entityToken: sc.startPoint})
            MATCH (sp2 {entityToken: sc.endPoint})
            MERGE (sc)-[:STARTS_AT]->(sp1)
            MERGE (sc)-[:ENDS_AT]->(sp2)
            """,
            'profile_contains': r"""
            MATCH (s:`Sketch`)-[:CONTAINS]->(p:`Profile`)
            WHERE p.profileCurves IS NOT NULL
            UNWIND p.profileCurves AS curve_token
            MATCH (sc {entityToken: curve_token})
            MERGE (p)-[:CONTAINS]->(sc)
            """,
            'sketch_lines': r"""
            MATCH (sc:`SketchLine`)
            WHERE sc.startPoint IS NOT NULL AND sc.endPoint IS NOT NULL

            // Ensure that the startPoint and endPoint nodes exist
            WITH sc, sc.startPoint AS startPointToken, sc.endPoint AS endPointToken
            MATCH (sp1 {entityToken: startPointToken})
            MATCH (sp2 {entityToken: endPointToken})

            // Create relationships
            MERGE (sc)-[:STARTS_AT]->(sp1)
            MERGE (sc)-[:ENDS_AT]->(sp2)

            RETURN sc, sp1, sp2
            """,
            'circle_center': r"""
            MATCH (circle)
            WHERE circle.centerPoint IS NOT NULL
            MATCH (center {entityToken: circle.centerPoint})
            MERGE (circle)-[:CENTERED_ON]->(center)
            REMOVE circle.centerPoint
            RETURN circle, center
            """,
            'projection': r"""
            MATCH (se:SketchEntity)
            WHERE se.referencedEntity IS NOT NULL
            MATCH (re:SketchEntity)
            WHERE re.entityToken = se.referencedEntity
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
    
    def create_sketch_dimensions_relationships(self):
        """
        Creates 'DIMENSIONED' relationships between sketch entities and their corresponding dimensions.

        This function connects any node with a sketchDimensions property to all the SketchDimension nodes
        that share the same entityToken as the ones in the list under the sketchDimensions property.

        Returns:
            list: The result values from the query execution.
        """
        cypher_queries = [
            """
            MATCH (d)
            WHERE ('SketchDimension' IN labels(d) OR 'SketchLinearDimension' IN labels(d)) 
                AND d.entityOne IS NOT NULL 
                AND d.entityTwo IS NOT NULL
            MATCH (a {entityToken: d.entityOne})
            MATCH (b {entityToken: d.entityTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.entityOne, d.entityTwo
            """,
            """
            MATCH (d)
            WHERE (d:SketchAngularDimension) 
                AND d.lineOne IS NOT NULL 
                AND d.lineTwo IS NOT NULL
            MATCH (a {entityToken: d.lineOne})
            MATCH (b {entityToken: d.lineTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.lineOne, d.lineTwo
            """,   
            """
            MATCH (d)
            WHERE (d:SketchConcentricCircleDimension) 
                AND d.circleOne IS NOT NULL 
                AND d.circleTwo IS NOT NULL
            MATCH (a {entityToken: d.circleOne})
            MATCH (b {entityToken: d.circleTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.circleOne, d.circleTwo
            """,   
            """
            MATCH (d)
            WHERE ('SketchDiameterDimension' IN labels(d) OR 'SketchRadialDimension' IN labels(d))
                AND d.entity IS NOT NULL 
            MATCH (a {entityToken: d.entity})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(a)
            REMOVE d.entity
            """,
            """
            MATCH (d)
            WHERE (d:SketchDistanceBetweenLineAndPlanarSurfaceDimension) 
                AND d.line IS NOT NULL 
                AND d.planarSurface IS NOT NULL
            MATCH (a {entityToken: d.line})
            MATCH (b {entityToken: d.planarSurface})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.line, d.planarSurface
            """,   
            """
            MATCH (d)
            WHERE (d:SketchDistanceBetweenPointAndSurfaceDimension) 
                AND d.point IS NOT NULL 
                AND d.surface IS NOT NULL
            MATCH (a {entityToken: d.point})
            MATCH (b {entityToken: d.surface})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.point, d.surface
            """,   
            """
            MATCH (d)
            WHERE (d:SketchLinearDiameterDimension) 
                AND d.line IS NOT NULL 
                AND d.entityTwo IS NOT NULL
            MATCH (a {entityToken: d.line})
            MATCH (b {entityToken: d.entityTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.line, d.entityTwo
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetCurvesDimension) 
                AND d.offsetConstraint IS NOT NULL 
            MATCH (c {entityToken: d.offsetConstraint})
            MERGE (c)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.offsetConstraint
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetCurvesDimension) 
                AND d.offsetConstraint IS NOT NULL 
            MATCH (c {entityToken: d.offsetConstraint})
            MERGE (c)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.offsetConstraint
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetDimension) 
                AND d.line IS NOT NULL 
                AND d.entityTwo IS NOT NULL 
            MATCH (a {entityToken: d.line})
            MATCH (c {entityToken: d.entityTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.line, d.entityTwo
            """,
            #  Redundancy check for Circle entities dimensions
            """
            // Query to create DIMENSIONED relationships using the dimensions property of SketchCircle

            // Unwind dimensions and create DIMENSIONED relationships from dimension to circle
            MATCH (circle:SketchCircle)
            UNWIND circle.dimensions AS dimension_id
            MATCH (dim:SketchDimension {entityToken: dimension_id})
            WHERE NOT (dim)-[:DIMENSIONED]->(circle)
            MERGE (dim)-[:DIMENSIONED]->(circle)
            RETURN circle, dim;
            """,
            """
            // Unwind dimensions and create DIMENSIONED relationships from circle to dimension
            MATCH (circle:SketchCircle)
            UNWIND circle.dimensions AS dimension_id
            MATCH (dim:SketchDimension {entityToken: dimension_id})
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
            WHERE c.entities IS NOT NULL AND c.createdEntities IS NOT NULL AND c.centerPoint IS NOT NULL
            UNWIND c.entities AS entity_token
            MATCH (se {entityToken: entity_token}) // Source Entities
            WITH c, se
            UNWIND c.createdEntities AS created_entity_token
            MATCH (te {entityToken: created_entity_token}) // Target Entities
            WITH c, se, te
            MATCH (ce {entityToken: c.centerPoint}) // Center Point
            MERGE (se)-[:CONSTRAINED]->(c)
            MERGE (c)-[:CONSTRAINED]->(te)
            MERGE (ce)-[:CONSTRAINED]->(c)
            REMOVE c.entities, c.createdEntities, c.centerPoint
            RETURN c, se, te, ce
            """,
            # Creates relationships for VerticalConstraint entities with yAxis.
            """   
            MATCH (vc:VerticalConstraint)
            WHERE vc.line IS NOT NULL
            UNWIND vc.line AS entity_token
            MATCH (se {entityToken: entity_token}) // Source Entities
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
            MATCH (se {entityToken: entity_token}) // Source Entities
            MATCH (sa:SketchAxis {name: 'x'}) // Target SketchAxis
            WITH hc, se, sa
            MATCH (hc)<-[:CONTAINS]-(s:Sketch)-[:CONTAINS]->(sa)
            MERGE (se)-[:CONSTRAINED]->(hc)
            MERGE (hc)-[:CONSTRAINED]->(sa)
            // REMOVE hc.line
            RETURN hc, se, sa
            """,
            # Creates relationships for PerpendicularConstraint entities linking lineOne and lineTwo.
            """
            MATCH (pc:PerpendicularConstraint)
            WHERE pc.lineOne IS NOT NULL AND pc.lineTwo IS NOT NULL
            MATCH (source {entityToken: pc.lineOne}) // Source Entity
            MATCH (target {entityToken: pc.lineTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(pc)
            MERGE (pc)-[:CONSTRAINED]->(target)
            REMOVE pc.lineOne, pc.lineTwo
            RETURN pc, source, target
            """,
            # Creates relationships for CoincidentConstraint entities linking point and entity.
            """
            MATCH (cc:CoincidentConstraint)
            WHERE cc.point IS NOT NULL AND cc.entity IS NOT NULL
            MATCH (source {entityToken: cc.point}) // Source Entity
            MATCH (target {entityToken: cc.entity}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(cc)
            MERGE (cc)-[:CONSTRAINED]->(target)
            REMOVE cc.point, cc.entity
            RETURN cc, source, target
            """,
            # Creates relationships for CollinearConstraint entities linking lineOne and lineTwo.
            """
            MATCH (cc:CollinearConstraint)
            WHERE cc.lineOne IS NOT NULL AND cc.lineTwo IS NOT NULL
            MATCH (source {entityToken: cc.lineOne}) // Source Entity
            MATCH (target {entityToken: cc.lineTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(cc)
            MERGE (cc)-[:CONSTRAINED]->(target)
            REMOVE cc.lineOne, cc.lineTwo
            RETURN cc, source, target
            """,
            # Creates relationships for EqualConstraint entities linking curveOne and curveTwo.
            """
            MATCH (ec:EqualConstraint)
            WHERE ec.curveOne IS NOT NULL AND ec.curveTwo IS NOT NULL
            MATCH (source {entityToken: ec.curveOne}) // Source Entity
            MATCH (target {entityToken: ec.curveTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(ec)
            MERGE (ec)-[:CONSTRAINED]->(target)
            REMOVE ec.curveOne, ec.curveTwo
            RETURN ec, source, target
            """,
            # Creates relationships for ParallelConstraint entities linking lineOne and lineTwo.
            """
            MATCH (pc:ParallelConstraint)
            WHERE pc.lineOne IS NOT NULL AND pc.lineTwo IS NOT NULL
            MATCH (source {entityToken: pc.lineOne}) // Source Entity
            MATCH (target {entityToken: pc.lineTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(pc)
            MERGE (pc)-[:CONSTRAINED]->(target)
            REMOVE pc.lineOne, pc.lineTwo
            RETURN pc, source, target
            """,
            # reates relationships for SymmetryConstraint entities linking entityOne, entityTwo, and symmetry_line.
            """
            MATCH (sc:SymmetryConstraint)
            WHERE sc.entityOne IS NOT NULL AND sc.entityTwo IS NOT NULL AND sc.symmetry_line IS NOT NULL
            MATCH (source {entityToken: sc.entityOne}) // Source Entity
            MATCH (target {entityToken: sc.entityTwo}) // Target Entity
            MATCH (symmetry_line {entityToken: sc.symmetry_line}) // Symmetry Line
            MERGE (source)-[:CONSTRAINED]->(sc)
            MERGE (sc)-[:CONSTRAINED]->(target)
            MERGE (symmetry_line)-[:CONSTRAINED]->(sc)
            REMOVE sc.entityOne, sc.entityTwo, sc.symmetry_line
            RETURN sc, source, target, symmetry_line
            """,
            # Creates relationships for TangentConstraint entities linking curveOne and curveTwo.
            """
            MATCH (tc:TangentConstraint)
            WHERE tc.curveOne IS NOT NULL AND tc.curveTwo IS NOT NULL
            MATCH (source {entityToken: tc.curveOne}) // Source Entity
            MATCH (target {entityToken: tc.curveTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(tc)
            MERGE (tc)-[:CONSTRAINED]->(target)
            REMOVE tc.curveOne, tc.curveTwo
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
            WITH sketch, sketch.origin AS origin_position, sketch.x_direction AS x_axis_vector, sketch.y_direction AS y_axis_vector, sketch.origin_point AS origin_entityToken
            MERGE (origin:SketchEntity {entityToken: origin_entityToken})
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

    transformer = Neo4jTransformerOrchestrator(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        nodes = transformer.create_timeline_relationships()
        for record in nodes:
            print(record)
        transformer.create_face_adjacencies()
    finally:
        transformer.close()

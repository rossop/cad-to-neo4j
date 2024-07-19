"""
BRep Relationships Transformer

This module provides the transformation logic for BRep relationships.

Classes:
    - BRepTransformer: A class to handle BRep-based transformations.
"""
import traceback
from ..base_transformer import BaseTransformer

class BRepTransformer(BaseTransformer):
    """
    BRepTransformer

    A class to handle BRep-based transformations.

    Methods:
        transform(execute_query): Runs all BRep-related transformation methods.
    """
    def transform(self, execute_query):
        """
        Runs all BRep-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_brep_relationships'] = self.create_brep_relationships(execute_query)
        results['create_brep_face_relationships'] = self.create_brep_face_relationships(execute_query)
        return results

    def create_brep_relationships(self, execute_query):
        """
        Creates relationships between BRep entities.

        Args:
            execute_query (function): Function to execute a Cypher query.

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
                results.extend(execute_query(query))
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results

    def create_brep_face_relationships(self, execute_query):
        """
        Creates relationships between BRepEdge nodes and their vertices.

        This method creates 'BOUNDED_BY' relationships between BRepEdge nodes and their start and end vertices.
        The 'BOUNDED_BY' relationship will have a type property indicating whether it is a 'START_WITH' or 'ENDS_WITH' relationship.

        Args:
            execute_query (function): Function to execute a Cypher query.

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
        ]
        results = []
        self.logger.info('Creating BRep face relationships')
        for query in queries:
            try:
                results.extend(execute_query(query))
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results
    
    def create_brep_adjacencies(self, execute_query):
        """
        Creates 'ADJACENT' relationships between BRep faces sharing the same edge
        and BRep edges sharing the same vertex.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            # Query to create ADJACENT relationships between faces sharing the same edge
            """
            MATCH (e:`BRepEdge`)<-[:CONTAINS]-(f1:`BRepFace`), 
                  (e)<-[:CONTAINS]-(f2:`BRepFace`)
            WHERE id(f1) <> id(f2)
            MERGE (f1)-[:ADJACENT]->(f2)
            MERGE (f2)-[:ADJACENT]->(f1)
            RETURN f1.entityToken AS face1_id, f2.entityToken AS face2_id
            """,
            # Query to create ADJACENT relationships between edges sharing the same vertex
            """
            MATCH (v:`BRepVertex`)<-[:CONTAINS]-(e1:`BRepEdge`), 
                  (v)<-[:CONTAINS]-(e2:`BRepEdge`)
            WHERE id(e1) <> id(e2)
            MERGE (e1)-[:ADJACENT]->(e2)
            MERGE (e2)-[:ADJACENT]->(e1)
            RETURN e1.entityToken AS edge1_id, collect(e2.entityToken) AS adjacent_edge_ids
            """
        ]
        
        results = []
        self.logger.info('Creating BRep adjacencies')
        for query in queries:
            try:
                results.extend(execute_query(query))
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results
# cad_to_neo4j/trasform/core/strategie
from typing import List

from ..base_transformer import BaseTransformer
from ....utils.cypher_utils import helper_cypher_error


class BRepChangeTransformer(BaseTransformer):
    """
    BRepChangeTransformer

    A transformer class to detect and manage BRepFace transformations
    across non-continuous timelinePosition ranges.

    Methods:
        transform(execute_query): Runs the transformation logic to detect
        face transformations and manage related relationships.
    """

    def transform(self, execute_query):
        """
        Detect and update face transformations in the timeline.

        Args:
            execute_query (function): Function to execute Cypher queries.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_timeline_temporary_nodes'] = \
            self.create_timeline_temporary_nodes(execute_query)
        results['create_face_relationship_nodes'] = \
            self.create_face_relationship_nodes(execute_query)
        results['detect_face_transformations'] = \
            self.detect_face_transformations(execute_query)
        results['delete_temporary_nodes'] = \
            self.delete_temporary_nodes(execute_query)
        return results

    @helper_cypher_error
    def get_max_timeline_position(self, execute_query):
        """
        Retrieve the maximum value of `timelinePosition` from the Neo4j
        database.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            int: The maximum `timelinePosition` value found.
        """
        max_timeline_query = """
        MATCH (e)
        WHERE e.timelinePosition IS NOT NULL
        RETURN MAX(e.timelinePosition) AS maxPosition
        """

        # Execute the query and fetch the result
        result = execute_query(max_timeline_query)

        # Assuming result is returned as a list of dictionaries
        if result and len(result) > 0:
            return int(result[0][0])

        # If no result found, return None
        return None

    @helper_cypher_error
    def create_timeline_temporary_nodes(self, execute_query):
        """
        Create temporary nodes for integer values starting from zero and
        incrementing. Each node is linked to BRep entities (faces, edges, and
        vertices) that satisfy the WHERE condition on timelinePosition.

        Args:
            execute_query (function): Function to execute a Cypher query.
            start_position (int): The starting position for the timeline nodes
            (default is 0).

        Returns:
            None
        """
        self.logger.info('Creating temporary timeline nodes...')

        max_val = self.get_max_timeline_position(execute_query)
        if max_val is None:
            return None

        positions: List[int] = []

        for position in range(max_val + 1):
            create_temp_nodes_query = """
            MATCH (e:BRepFace)
            WHERE $position IN e.timelinePosition
                OR e.timelinePosition = $position
            MERGE (tp:TemporaryTimeline {position: $position})
            MERGE (e)-[:EXISTS_AT]->(tp)
            RETURN e.entityToken, tp.position
            """
            result = execute_query(
                create_temp_nodes_query, {'position': position})

            if len(result) > 0:
                positions.append(position)

        for i in range(len(positions) - 1):
            current_position = positions[i]
            next_position = positions[i + 1]

            link_timeline_nodes_query = """
            MATCH (tp1:TemporaryTimeline {position: $current_position})
            MATCH (tp2:TemporaryTimeline {position: $next_position})
            MERGE (tp1)-[:NEXT]->(tp2)
            """
            execute_query(
                link_timeline_nodes_query,
                {'current_position': current_position,
                 'next_position': next_position}
            )

        return positions

    def delete_temporary_nodes(self, execute_query):
        """
        Delete the temporary nodes created for timeline analysis.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            None
        """
        self.logger.info('Deleting temporary timeline nodes...')
        delete_temp_nodes_query = """
        MATCH (t:TemporaryTimeline|TemporaryType)
        DETACH DELETE t
        """
        return execute_query(delete_temp_nodes_query)

    def create_face_relationship_nodes(self, execute_query):
        """
        Create nodes to classify face relationships as 'sideFaces',
        'startFaces', 'endFaces', or 'Others' based on the 'BOUNDED_BY'
        relationship type.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            None
        """
        classification_queries = [
            # Handle sideFaces relationship
            """
            MATCH (f:BRepFace)<-[r:BOUNDED_BY]-(feature)
            WHERE r.type = 'sideFaces'
            MERGE (side:TemporaryType {name: 'Side'})
            MERGE (f)-[:BELONGS_TO]->(side)
            RETURN f, side
            """,
            # Handle startFaces relationship
            """
            MATCH (f:BRepFace)<-[r:BOUNDED_BY]-(feature)
            WHERE r.type = 'startFaces'
            MERGE (start:TemporaryType {name: 'Start'})
            MERGE (f)-[:BELONGS_TO]->(start)
            RETURN f, start
            """,
            # Handle endFaces relationship
            """
            MATCH (f:BRepFace)<-[r:BOUNDED_BY]-(feature)
            WHERE r.type = 'endFaces'
            MERGE (end:TemporaryType {name: 'End'})
            MERGE (f)-[:BELONGS_TO]->(end)
            RETURN f, end
            """,
            # Handle null or other relationships
            """
            MATCH (f:BRepFace)<-[r:BOUNDED_BY]-(feature)
            WHERE r.type IS NULL OR
                NOT r.type IN ['sideFaces', 'startFaces', 'endFaces']
            MERGE (other:TemporaryType {name: 'Others'})
            MERGE (f)-[:BELONGS_TO]->(other)
            RETURN f, other
            """
        ]
        results = []
        for query in classification_queries:
            result = execute_query(query)
            results.append(result)
        return results

    @helper_cypher_error
    def detect_face_transformations(self, execute_query):
        """
        Detect transformations of faces between timeline steps, accounting for
        non-continuous timeline positions.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        # First, create temporary nodes for analysis
        self.create_timeline_temporary_nodes(execute_query)

        # Detect transformations using face and edge relationships
        transformation_query = """
        MATCH
            (f1:BRepFace)-[:EXISTS_AT]->(tt1:TemporaryTimeline),
            (f2:BRepFace)-[:EXISTS_AT]->(tt2:TemporaryTimeline),
            // Ensure consecutiveness
            (tt1)-[:NEXT]->(tt2),
            (f1)-[:CONTAINS]->(e:BRepEdge),
            (f2)-[:CONTAINS]->(e)
        // Ensure non overlapping
        WHERE NOT (f1)-[:EXISTS_AT]->(tt2)
            AND NOT (f2)-[:EXISTS_AT]->(tt1)
        WITH f1, f2
        MERGE (f1)-[:TRANSFORMED_INTO]->(f2)
        RETURN f1.entityToken AS face1, f2.entityToken AS face2
        """
        transformation_results = execute_query(transformation_query)
        transformation_msg: str = "Linked Transformed Faces"
        self.logger.info(transformation_msg)
        # Clean up temporary nodes
        self.delete_temporary_nodes(execute_query)

        return transformation_results

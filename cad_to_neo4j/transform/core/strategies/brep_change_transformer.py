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

        self.logger.debug(positions)
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
        delete_temp_nodes_query = """
        MATCH (t:TemporaryTimeline)
        DETACH DELETE t
        """
        execute_query(delete_temp_nodes_query)

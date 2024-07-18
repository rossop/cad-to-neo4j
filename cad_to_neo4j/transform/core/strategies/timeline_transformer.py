"""
Timeline Relationships Transformer

This module provides the transformation logic for timeline relationships.

Classes:
    - TimelineTransformer: A class to handle timeline-based transformations.
"""

from ..base_transformer import BaseTransformer

class TimelineTransformer(BaseTransformer):
    """
    TimelineTransformer

    A class to handle timeline-based transformations.

    Methods:
        transform(execute_query): Runs all timeline-related transformation methods.
    """
    def transform(self, execute_query):
        """
        Runs all timeline-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_timeline_relationships'] = self.create_timeline_relationships(execute_query)
        return results

    def create_timeline_relationships(self, execute_query):
        """
        Creates relationships between nodes based on their timeline index.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        cypher_query = """
        MATCH (n)
        WHERE n.timelineIndex IS NOT NULL
        WITH n
        ORDER BY n.timelineIndex ASC
        WITH collect(n) AS nodes
        UNWIND range(0, size(nodes) - 2) AS i
        WITH nodes[i] AS node1, nodes[i + 1] AS node2
        MERGE (node1)-[:NEXT_ON_TIMELINE]->(node2)
        RETURN node1, node2
        """
        self.logger.info('Creating timeline relationships')
        return execute_query(cypher_query)

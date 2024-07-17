"""
Component Relationships Transformer

This module provides the transformation logic for component relationships.

Classes:
    - ComponentTransformer: A class to handle component-based transformations.
"""
import traceback
from ..base_transformer import BaseTransformer

class ComponentTransformer(BaseTransformer):
    """
    ComponentTransformer

    A class to handle component-based transformations.

    Methods:
        transform(execute_query): Runs all component-related transformation methods.
    """
    def transform(self, execute_query):
        """
        Runs all component-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_component_relationships'] = self.create_component_relationships(execute_query)
        return results

    def create_component_relationships(self, execute_query):
        """
        Creates relationships between components and other entities.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            """
            MATCH (e)
            WHERE ('Sketch' IN labels(e) 
                OR 'Feature' IN labels(e)) 
                AND e.parentComponent IS NOT NULL
            WITH e.parentComponent AS component_token, e
            MATCH (c:Component {entityToken: component_token})
            MERGE (c)-[:CONTAINS]->(e)
            RETURN c, e
            """,
        ]
        results = []
        self.logger.info('Creating component relationships')
        for query in queries:
            try:
                results.extend(execute_query(query))
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results

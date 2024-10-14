"""
Component Relationships Transformer

This module provides the transformation logic for component relationships.

Classes:
    - ComponentTransformer: A class to handle component-based transformations.
"""
from ..base_transformer import BaseTransformer
from ....utils.cypher_utils import helper_cypher_error


class ComponentTransformer(BaseTransformer):
    """
    ComponentTransformer

    A class to handle component-based transformations.

    Methods:
        transform(execute_query): Runs all component-related transformation
        methods.
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
        results['create_component_relationships'] =\
            self.create_component_relationships(execute_query)
        results['create_sketches_to_planes_relationship'] =\
            self.create_sketches_to_planes_relationship(execute_query)
        results['create_contains_relationships'] =\
            self.create_contains_relationships(execute_query)
        results['create_parameter_relationships'] =\
            self.create_parameter_relationships(execute_query)
        return results

    @helper_cypher_error
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
            results.extend(execute_query(query))
        return results

    @helper_cypher_error
    def create_sketches_to_planes_relationship(self, execute_query):
        """
        Creates 'BUILT_ON' relationships between sketches and their reference
        planes or faces.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            r"""
            MATCH (s:`Sketch`)
            WHERE s.reference_plane_entity_token IS NOT NULL
            MATCH (p {entityToken: s.reference_plane_entity_token})
            MERGE (s)-[:BUILT_ON]->(p)
            RETURN s.entityToken AS sketch_id,
                p.entityToken AS plane_id,
                labels(p) AS plane_labels
            """,
        ]

        results = []
        self.logger.info('Creating sketch to plane/face relationships')
        for query in queries:
            results.extend(execute_query(query))
        return results

    @helper_cypher_error
    def create_contains_relationships(self, execute_query):
        """
        Creates 'CONTAINS' relationships between root components and their
        child components using the rootComponentToken property.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        query = """
        MATCH (childComponent:Component)
        WHERE childComponent.rootComponentToken IS NOT NULL
        MATCH (rootComponent:Component {
            entityToken: childComponent.rootComponentToken})
        MERGE (rootComponent)-[:CONTAINS]->(childComponent)
        RETURN rootComponent, childComponent
        """
        results = []
        self.logger.info(
            'Creating CONTAINS relationships between root components'
            'and child components')
        results = execute_query(query)
        return results

    @helper_cypher_error
    def create_parameter_relationships(self, execute_query):
        """
        Creates relationships between parameters and the components or
        features they belong to.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            """
            MATCH (p:Parameter)
            WHERE p.parentComponent IS NOT NULL
            MATCH (c:Component {entityToken: p.parentComponent})
            MERGE (c)-[:HAS_PARAMETER]->(p)
            RETURN c, p
            """,
            """
            MATCH (p:Parameter)
            WHERE p.createdBy IS NOT NULL
            MATCH (e {entityToken: p.createdBy})
            MERGE (e)-[:HAS_PARAMETER]->(p)
            RETURN e, p
            """
        ]

        results = []
        self.logger.info(
            'Creating relationships between parameters and '
            'their parent components or features')

        for query in queries:
            results.extend(execute_query(query))

        return results

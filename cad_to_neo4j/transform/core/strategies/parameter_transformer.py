"""
Parameter Transformer Module.

This module provides the transformation logic for linking parameters in the
Neo4j graph database. The ParameterTransformer class is designed to create
relationships between parameters based on their dependencies and dependents.
It utilizes the entityTokens of parameters to establish these relationships.

The transformer can link:
    - Parameters that are **dependent** on other parameters.
    - Parameters that have **dependencies** on other parameters.

Classes:
--------
- `ParameterTransformer`: A transformer class that handles
    parameter-to-parameter relationships, including dependent and dependency
    links.

Methods:
--------
- `transform(execute_query)`: Runs all parameter-related transformations. It
    executes queries to link dependent and dependency parameters.
- `link_parameters(execute_query)`: Executes Cypher queries to link parameters
    based on their dependent and dependency parameters using entityTokens.

Decorators:
-----------
- `@helper_cypher_error`: A decorator used to handle errors during Cypher
    query execution in the `link_parameters` method. It captures and logs
    exceptions to ensure that the transformation process continues even if
    individual queries fail.

Usage:
------
This transformer is used to create relationships between parameters, linking
them through the entityToken of their dependent and dependency parameters.
The resulting relationships will be stored in the Neo4j graph database,
enabling easy querying of parameter dependencies and relationships.

Relationships:
--------------
- `HAS_DEPENDENT`: Created between a parameter and its dependent parameters.
- `DEPENDENT_ON`: Created between a parameter and the parameters it depends on.
"""

from ..base_transformer import BaseTransformer
from ....utils.cypher_utils import helper_cypher_error


class ParameterTransformer(BaseTransformer):
    """
    ParameterTransformer

    A class to handle parameter-based transformations, specifically linking
    parameters to their dependencies and dependents.

    Methods:
        transform(execute_query): Runs all parameter-related transformation
            methods.
        link_parameters(execute_query): Links parameters using entityTokens.
    """

    def transform(self, execute_query):
        """
        Runs all parameter-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['link_parameters'] = self.link_parameters(execute_query)
        results['link_created_by_relationship'] = \
            self.link_created_by_relationship(execute_query)
        return results

    @helper_cypher_error
    def link_parameters(self, execute_query):
        """
        Links parameters to their dependent and dependency parameters based
        on their entityTokens.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            # Link dependent parameters
            """
            MATCH (p:Parameter)
            WHERE p.dependentParameters IS NOT NULL
            UNWIND p.dependentParameters AS dependent_param_token
            MATCH (dp:Parameter {entityToken: dependent_param_token})
            MERGE (p)-[:HAS_DEPENDENT]->(dp)
            RETURN p.entityToken AS param_id,
                collect(dp.entityToken) AS dependent_params
            """,
            # Link dependency parameters
            """
            MATCH (p:Parameter)
            WHERE p.dependencyParameters IS NOT NULL
            UNWIND p.dependencyParameters AS dependency_param_token
            MATCH (dp:Parameter {entityToken: dependency_param_token})
            MERGE (p)-[:DEPENDENT_ON]->(dp)
            RETURN p.entityToken AS param_id,
                collect(dp.entityToken) AS dependency_params
            """
        ]
        results = []
        self.logger.info('Linking parameters to dependents and dependencies')
        for query in queries:
            results.extend(execute_query(query))
        return results

    @helper_cypher_error
    def link_created_by_relationship(self, execute_query):
        """
        Links parameters to the object that created them (e.g., a feature,
        sketch dimension).

        Args:
            execute_query (function): Function to execute Cypher queries.

        Returns:
            list: A list of results from the executed query.
        """
        query = """
        MATCH (p:Parameter)
        WHERE p.createdBy IS NOT NULL
        MATCH (creator {entityToken: p.createdBy})
        MERGE (p)-[:CREATED_BY]->(creator)
        RETURN p.entityToken AS parameter_id, creator.entityToken AS creator_id
        """
        return execute_query(query)

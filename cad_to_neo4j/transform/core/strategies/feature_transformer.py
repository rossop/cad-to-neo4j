"""
Feature Relationships Transformer

This module provides the transformation logic for feature relationships.

Classes:
    - FeatureTransformer: A class to handle feature-based transformations.
"""

from ..base_transformer import BaseTransformer
from ....utils.cypher_utils import helper_cypher_error


class FeatureTransformer(BaseTransformer):
    """
    FeatureTransformer

    A class to handle feature-based transformations.

    Methods:
        transform(execute_query): Runs all feature-related transformation
            methods.
        create_profile_relationships(execute_query): Creates 'USES_PROFILE'
            relationships between features and profiles.
        link_feature_to_extents_and_faces(execute_query): Links features to
            their extents and faces based on various properties.
        link_feature_to_linked_features_and_parameters(execute_query): Links
            features to linked features and taper angles to parameters.
    """
    def transform(self, execute_query):
        """
        Runs all feature-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_profile_relationships'] = \
            self.create_profile_relationships(execute_query)
        results['create_feature_to_extents_and_faces_relationships'] = \
            self.create_feature_to_extents_and_faces_relationships(
                execute_query)
        results['link_taper_angles_to_parameters'] = \
            self.link_taper_angles_to_parameters(execute_query)
        results['link_feature_to_linked_features_and_parameters'] =\
            self.link_feature_to_linked_features_and_parameters(execute_query)
        return results

    @helper_cypher_error
    def create_profile_relationships(self, execute_query):
        """
        Creates 'USES_PROFILE' relationships between feature and profiles based
        on the profileTokens list.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            """
            MATCH (f:Feature)
            WHERE f.profileTokens IS NOT NULL
            UNWIND f.profileTokens AS profile_token
            MATCH (p:Profile)
            WHERE p.entityToken = profile_token
            MERGE (f)-[:USES_PROFILE]->(p)
            RETURN
                f.entityToken AS feature_id,
                collect(p.entityToken) AS profile_ids
            """,
            ]
        results = []
        self.logger.info('Creating profile/feature relationships')
        for query in queries:
            results.extend(execute_query(query))
        return results

    @helper_cypher_error
    def create_feature_to_extents_and_faces_relationships(self, execute_query):
        """
        Links features to their extents and faces based on various properties.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            """
            MATCH (f)
            WHERE f.extentOne IS NOT NULL OR f.extentTwo IS NOT NULL
            OPTIONAL MATCH (e1 {entityToken: f.extentOne_object_id})
            OPTIONAL MATCH (e2 {entityToken: f.extentTwo_object_id})

            FOREACH (ignore IN CASE WHEN f.extentOne_object_id IS NOT NULL
                THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_extentOne]->(e1)
            )
            FOREACH (ignore IN CASE WHEN f.extentTwo_object_id IS NOT NULL
                THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_extentTwo]->(e2)
            )

            WITH f
            OPTIONAL MATCH (sf {entityToken: f.startFaces})
            OPTIONAL MATCH (ef {entityToken: f.endFaces})
            OPTIONAL MATCH (sif {entityToken: f.sideFaces})

            FOREACH (ignore IN CASE WHEN f.startFaces IS NOT NULL
                THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_START_FACE]->(sf)
            )
            FOREACH (ignore IN CASE WHEN f.endFaces IS NOT NULL
                THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_END_FACE]->(ef)
            )
            FOREACH (ignore IN CASE WHEN f.sideFaces IS NOT NULL
                THEN [1] ELSE [] END |
                MERGE (f)-[:HAS_SIDE_FACE]->(sif)
            )

            RETURN f.entityToken AS feature_id,
                f.extentOne_object_id AS extentOne_id,
                f.extentTwo_object_id AS extentTwo_id,
                f.startFaces AS startFaces,
                f.endFaces AS endFaces,
                f.sideFaces AS sideFaces
            """,
        ]
        results = []
        tranformation_msg: str = \
            'Creating relationships between features, extents and faces'
        self.logger.info(tranformation_msg)
        for query in queries:
            results.extend(execute_query(query))
        return results

    @helper_cypher_error
    def link_taper_angles_to_parameters(self, execute_query):
        """
        Links the taper angles of extrude features to their corresponding model
        parameters.

        Args:
            execute_query (function): Function to execute a Cypher query.
        """
        queries = [
            """
            MATCH (f:Feature)
            WHERE f.taperAngleOne IS NOT NULL
            MATCH (p:ModelParameter {entityToken: f.taperAngleOne})
            MERGE (f)-[:USES_PARAMETER]->(p)
            RETURN f.entityToken AS feature_id, p.entityToken AS parameter_id
            """,
            """
            MATCH (f:Feature)
            WHERE f.taperAngleTwo IS NOT NULL
            MATCH (p:ModelParameter {entityToken: f.taperAngleTwo})
            MERGE (f)-[:USES_PARAMETER]->(p)
            RETURN f.entityToken AS feature_id, p.entityToken AS parameter_id
            """
        ]
        results = []
        self.logger.info('Linking taper angles to parameters')
        for query in queries:
            results.extend(execute_query(query))
        return results

    @helper_cypher_error
    def link_feature_to_linked_features_and_parameters(self, execute_query):
        """
        Links features to linked features and taper angles to model parameters.
        """
        queries = [
            """
            MATCH (f:Feature)
            WHERE f.linkedFeatures IS NOT NULL
            UNWIND f.linkedFeatures AS linkedFeature
            MATCH (lf {entityToken: linkedFeature})
            MERGE (f)-[:LINKED_TO]->(lf)
            RETURN f.entityToken AS feature_id,
                collect(lf.entityToken) AS linked_features
            """,
            """
            MATCH (f:Feature)
            WHERE f.taperAngleOne IS NOT NULL
            MATCH (p:ModelParameter {entityToken: f.taperAngleOne})
            MERGE (f)-[:USES_TAPER_ANGLE_ONE]->(p)
            RETURN f.entityToken AS feature_id, p.entityToken AS parameter_id
            """
        ]
        results = []
        self.logger.info('Linking features and taper angles')
        for query in queries:
            results.extend(execute_query(query))
        return results

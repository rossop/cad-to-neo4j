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
            // Query 1: Linking Untyped Faces
            MATCH (f:Feature)
            WHERE f.face IS NOT NULL
            UNWIND f.face AS faceToken
            OPTIONAL MATCH (unt:Face {entityToken: faceToken})
            FOREACH (ignore IN CASE WHEN unt IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[rel:HAS_FACE]->(unt)
                ON CREATE SET rel.type = NULL
            )
            RETURN f.entityToken AS feature_id,
                collect(faceToken) AS untyped_faces_linked
            """,
            """
            // Query 2: Linking Start Faces
            MATCH (f:Feature)
            WHERE f.startFaces IS NOT NULL
            UNWIND f.startFaces AS startFaceToken
            OPTIONAL MATCH (sf:Face {entityToken: startFaceToken})
            FOREACH (ignore IN CASE WHEN sf IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[rel:HAS_FACE]->(sf)
                // Overwrite if relationship already exists
                ON MATCH SET rel.type = 'start'
                ON CREATE SET rel.type = 'start'
            )
            RETURN f.entityToken AS feature_id,
                collect(startFaceToken) AS start_faces_linked
            """,
            """
            // Query 3: Linking End Faces
            MATCH (f:Feature)
            WHERE f.endFaces IS NOT NULL
            UNWIND f.endFaces AS endFaceToken
            OPTIONAL MATCH (ef:Face {entityToken: endFaceToken})
            FOREACH (ignore IN CASE WHEN ef IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[rel:HAS_FACE]->(ef)
                // Overwrite if relationship already exists
                ON MATCH SET rel.type = 'end'
                ON CREATE SET rel.type = 'end'
            )
            RETURN f.entityToken AS feature_id,
                collect(endFaceToken) AS end_faces_linked
            """,
            """
            // Query 4: Linking Side Faces
            MATCH (f:Feature)
            WHERE f.sideFaces IS NOT NULL
            UNWIND f.sideFaces AS sideFaceToken
            OPTIONAL MATCH (sif:Face {entityToken: sideFaceToken})
            FOREACH (ignore IN CASE WHEN sif IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[rel:HAS_FACE]->(sif)
                // Overwrite if relationship already exists
                ON MATCH SET rel.type = 'side'
                ON CREATE SET rel.type = 'side'
            )
            RETURN f.entityToken AS feature_id,
                collect(sideFaceToken) AS side_faces_linked
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
            WHERE f.extentOneTaperAngleToken IS NOT NULL
            OPTIONAL MATCH (p {entityToken: f.extentOneTaperAngleToken})
            MERGE (f)-[:USES_TAPER_ANGLE]->(p)
            RETURN f.entityToken AS feature_id,
                p.entityToken AS taper_angle_one_id
            """,
            """
            MATCH (f:Feature)
            WHERE f.extentTwoTaperAngleToken IS NOT NULL
            OPTIONAL MATCH (p {entityToken: f.extentTwoTaperAngleToken})
            MERGE (f)-[:USES_TAPER_ANGLE_TWO]->(p)
            RETURN f.entityToken AS feature_id,
                p.entityToken AS taper_angle_two_id
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
            // Query 1: Linking Features
            MATCH (f:Feature)
            WHERE f.linkedFeatures IS NOT NULL
            UNWIND f.linkedFeatures AS linkedFeature
            MATCH (lf {entityToken: linkedFeature})
            MERGE (f)-[:LINKED_TO]->(lf)
            RETURN f.entityToken AS feature_id,
                collect(lf.entityToken) AS linked_features

            """,
            """
            // Query 2: Linking Extent One (Entity-Based)
            MATCH (f:Feature)
            WHERE f.extentOneOffsetToken IS NOT NULL
                AND f.extentOneEntityToken IS NOT NULL
            OPTIONAL MATCH (e {entityToken: f.extentOneEntityToken})
            MERGE (f)-[rel:HAS_EXTENT {
                    type: 'ENTITY', order: 'extentOne'}]->(e)
            RETURN f.entityToken AS feature_id,
                e.entityToken AS extent_one_entity_id

            """,
            """
            // Query 3: Linking Extent Two (Entity-Based)
            MATCH (f:Feature)
            WHERE f.extentTwoOffsetToken IS NOT NULL
                AND f.extentTwoEntityToken IS NOT NULL
            OPTIONAL MATCH (e {entityToken: f.extentTwoEntityToken})
            MERGE (f)-[rel:HAS_EXTENT {
                type: 'ENTITY', order: 'extentTwo'}]->(e)
            RETURN f.entityToken AS feature_id,
                e.entityToken AS extent_two_entity_id
            """,
            # """
            # MATCH (f:Feature)
            # WHERE f.extentTwoOffsetToken IS NOT NULL
            # AND f.extentTwoEntityToken IS NOT NULL
            # OPTIONAL MATCH (e {entityToken: f.extentTwoEntityToken})
            # MERGE (f)-[:HAS_EXTENT]->(e)
            # RETURN f.entityToken AS feature_id,
            #     e.entityToken AS extent_two_entity_id
            # """,
            """
            // Query 4: Linking Distance One
            MATCH (f:Feature)
            WHERE f.extentOneDistanceToken IS NOT NULL
            OPTIONAL MATCH (p {entityToken: f.extentOneDistanceToken})
            MERGE (f)-[rel:HAS_EXTENT {
                type: 'DISTANCE', order: 'distanceOne'}]->(p)
            RETURN f.entityToken AS feature_id,
                p.entityToken AS distance_one_id
            """,
            """
            // Query 5: Linking Distance Two
            MATCH (f:Feature)
            WHERE f.extentTwoDistanceToken IS NOT NULL
            OPTIONAL MATCH (p {entityToken: f.extentTwoDistanceToken})
            MERGE (f)-[rel:HAS_EXTENT {
                type: 'DISTANCE', order: 'distanceTwo'}]->(p)
            RETURN f.entityToken AS feature_id,
                p.entityToken AS distance_two_id
            """,
        ]
        results = []
        self.logger.info('Linking features and taper angles')
        for query in queries:
            results.extend(execute_query(query))
        return results

"""
Construction Plane Relationships Transformer

This module provides the transformation logic for construction plane
relationships.

Classes:
    - ConstructionElementsTransformer: A class to handle construction
      plane-based transformations.
"""
from ..base_transformer import BaseTransformer
from ....utils.cypher_utils import helper_cypher_error


class ConstructionElementsTransformer(BaseTransformer):
    """
    ConstructionElementsTransformer

    A class to handle construction plane-based transformations.

    Methods:
        transform(execute_query): Runs all construction plane-related
        transformation methods.
    """
    def transform(self, execute_query):
        """
        Runs all construction plane-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_construction_planes_relationships'] = \
            self.create_construction_planes_relationships(execute_query)
        results['create_feature_to_axes_bodies_extents_relationships'] = \
            self.create_feature_to_axes_bodies_extents_relationships(
                execute_query)
        return results

    @helper_cypher_error
    def create_construction_planes_relationships(self, execute_query):
        """
        Creates relationships between construction planes and their defining
        entities.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            # parent
            """
            // Match existing ConstructionEntities nodes with
            // a non-null parentComponent
            MATCH (se)
            WHERE ('ConstructionPlane' IN labels(se)
                OR 'ConstructionAxis' IN labels(se)
                OR 'ConstructionPoint' IN labels(se))
                AND se.parent IS NOT NULL

            // Match existing Component node where entityToken matches
            // parent of ConstructionEntities
            MATCH (s:Component {entityToken: se.parent})

            // Create the relationship from Componenet to ConstructionEntities
            MERGE (s)-[:CONTAINS]->(se)
            """,
            # at_angle
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'AtAngle'})
            MATCH (linearEntity {entityToken: cp.linear_entity}),
                (planarEntity {entityToken: cp.planar_entity})
            MERGE (cp)-[:DEFINED_BY]->(linearEntity)
            MERGE (cp)-[:DEFINED_BY]->(planarEntity)
            RETURN cp.entityToken AS plane_id,
                linearEntity.entityToken AS linear_entity_id,
                planarEntity.entityToken AS planar_entity_id
            """,
            # by_plane
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'ByPlane'})
            MATCH (plane {entityToken: cp.plane})
            MERGE (cp)-[:DEFINED_BY]->(plane)
            RETURN cp.entityToken AS plane_id,
                plane.entityToken AS plane_entity_id
            """,
            # distance_on_path
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'DistanceOnPath'})
            MATCH (pathEntity {entityToken: cp.path_entity})
            MERGE (cp)-[:DEFINED_BY]->(pathEntity)
            RETURN cp.entityToken AS plane_id,
                pathEntity.entityToken AS path_entity_id
            """,
            # midplane
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'Midplane'})
            MATCH (planarEntityOne {entityToken: cp.planar_entityOne}),
            (planarEntityTwo {entityToken: cp.planar_entityTwo})
            MERGE (cp)-[:DEFINED_BY]->(planarEntityOne)
            MERGE (cp)-[:DEFINED_BY]->(planarEntityTwo)
            RETURN cp.entityToken AS plane_id,
                planarEntityOne.entityToken AS planar_entityOne_id,
                planarEntityTwo.entityToken AS planar_entityTwo_id
            """,
            # offset
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'Offset'})
            MATCH (planarEntity {entityToken: cp.planar_entity})
            MERGE (cp)-[:DEFINED_BY]->(planarEntity)
            RETURN cp.entityToken AS plane_id,
            planarEntity.entityToken AS planar_entity_id
            """,
            # tangent_at_point
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'TangentAtPoint'})
            MATCH (tangentFace {entityToken: cp.tangent_face}),
                (pointEntity {entityToken: cp.point_entity})
            MERGE (cp)-[:DEFINED_BY]->(tangentFace)
            MERGE (cp)-[:DEFINED_BY]->(pointEntity)
            RETURN cp.entityToken AS plane_id,
                tangentFace.entityToken AS tangent_face_id,
                pointEntity.entityToken AS point_entity_id
            """,
            # tangent
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'Tangent'})
            MATCH (tangentFace {entityToken: cp.tangent_face}),
                (planarEntity {entityToken: cp.planar_entity})
            MERGE (cp)-[:DEFINED_BY]->(tangentFace)
            MERGE (cp)-[:DEFINED_BY]->(planarEntity)
            RETURN cp.entityToken AS plane_id,
                tangentFace.entityToken AS tangent_face_id,
                planarEntity.entityToken AS planar_entity_id
            """,
            # three_points
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'ThreePoints'})
            MATCH (pointEntityOne {entityToken: cp.point_entityOne}),
                (pointEntityTwo {entityToken: cp.point_entityTwo}),
                (pointEntityThree {entityToken: cp.point_entity_three})
            MERGE (cp)-[:DEFINED_BY]->(pointEntityOne)
            MERGE (cp)-[:DEFINED_BY]->(pointEntityTwo)
            MERGE (cp)-[:DEFINED_BY]->(pointEntityThree)
            RETURN cp.entityToken AS plane_id,
                pointEntityOne.entityToken AS point_entityOne_id,
                pointEntityTwo.entityToken AS point_entityTwo_id,
                pointEntityThree.entityToken AS point_entity_three_id
            """,
            # two_edges
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'TwoEdges'})
            MATCH (linearEntityOne {entityToken: cp.linear_entityOne}),
                (linearEntityTwo {entityToken: cp.linear_entityTwo})
            MERGE (cp)-[:DEFINED_BY]->(linearEntityOne)
            MERGE (cp)-[:DEFINED_BY]->(linearEntityTwo)
            RETURN cp.entityToken AS plane_id,
                linearEntityOne.entityToken AS linear_entityOne_id,
                linearEntityTwo.entityToken AS linear_entityTwo_id
            """
        ]
        results = []
        self.logger.info('Creating construction plane relationships')
        for query in queries:
            results.extend(execute_query(query))
        return results

    @helper_cypher_error
    def create_feature_to_axes_bodies_extents_relationships(
            self, execute_query):
        """
        Creates relationships features to their axes, participant bodies, and
        extents based on various properties.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            # axis_relationships
            r"""
            MATCH (f)
            WHERE f.axisToken IS NOT NULL
            OPTIONAL MATCH (a {entityToken: f.axisToken})
            FOREACH (
                ignore IN CASE
                    WHEN f.axisToken IS NOT NULL
                    THEN [1]
                    ELSE []
                END |
                MERGE (f)-[:HAS_AXIS]->(a)
            )
            RETURN f.entityToken AS feature_id, f.axisToken AS axis_id
            """,
            # participant_body_relationships
            r"""
            MATCH (f)
            WHERE f.participantBodies IS NOT NULL
            UNWIND f.participantBodies AS body_token
            OPTIONAL MATCH (b {entityToken: body_token})
            WITH f, b, body_token WHERE b IS NOT NULL
            FOREACH (
                ignore IN CASE
                    WHEN body_token IS NOT NULL
                    THEN [1]
                    ELSE []
                END |
                MERGE (f)-[:HAS_PARTICIPANT_BODY]->(b)
            )
            RETURN f.entityToken AS feature_id,
                collect(b.entityToken) AS participant_body_ids
            """,
            # extentOne_relationships
            r"""
            MATCH (f)
            WHERE f.extentOne_object_id IS NOT NULL
            OPTIONAL MATCH (e1 {entityToken: f.extentOne_object_id})
            FOREACH (
                ignore IN CASE
                    WHEN f.extentOne_object_id IS NOT NULL
                    THEN [1]
                    ELSE []
                END |
                MERGE (f)-[:HAS_extentOne]->(e1)
            )
            RETURN f.entityToken AS feature_id,
                f.extentOne_object_id AS extentOne_id
            """,
            # extentTwo_relationships
            r"""
            MATCH (f)
            WHERE f.extentTwo_object_id IS NOT NULL
            OPTIONAL MATCH (e2 {entityToken: f.extentTwo_object_id})
            FOREACH (
                ignore IN CASE
                    WHEN f.extentTwo_object_id IS NOT NULL
                    THEN [1]
                    ELSE []
                END |
                MERGE (f)-[:HAS_extentTwo]->(e2)
            )
            RETURN f.entityToken AS feature_id,
                f.extentTwo_object_id AS extentTwo_id
            """
        ]

        results = []
        self.logger.info(
            'Linking features to axes, participant bodies, and extents')
        for query in queries:
            results.extend(execute_query(query))
        return results

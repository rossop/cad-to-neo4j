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
            OPTIONAL MATCH (linearEntity {entityToken: cp.linear_entity}),
                        (planarEntity {entityToken: cp.planar_entity})
            WITH cp, linearEntity, planarEntity
            WHERE linearEntity IS NOT NULL AND planarEntity IS NOT NULL
            MERGE (cp)-[:USES {type: 'at_angle',
                entity: 'linear'}]->(linearEntity)
            MERGE (cp)-[:USES {type: 'at_angle',
                entity: 'planar'}]->(planarEntity)
            RETURN cp.entityToken AS plane_id,
                linearEntity.entityToken AS linear_entity_id,
                planarEntity.entityToken AS planar_entity_id
            """,
            # by_plane
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'ByPlane'})
            OPTIONAL MATCH (plane {entityToken: cp.plane})
            WITH cp, plane
            WHERE plane IS NOT NULL
            MERGE (cp)-[:USES {type: 'by_plane', entity: 'plane'}]->(plane)
            RETURN cp.entityToken AS plane_id,
                plane.entityToken AS plane_entity_id
            """,]
        _ = [
            # distance_on_path
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'DistanceOnPath'})
            OPTIONAL MATCH (pathEntity {entityToken: cp.path_entity})
            WITH cp, pathEntity
            WHERE pathEntity IS NOT NULL
            MERGE (cp)-[:USES {type: 'distance_on_path',
                entity: 'path'}]->(pathEntity)
            RETURN cp.entityToken AS plane_id,
                pathEntity.entityToken AS path_entity_id
            """,
            # midplane
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'Midplane'})
            OPTIONAL MATCH (planarEntityOne {entityToken:cp.planar_entityOne}),
                        (planarEntityTwo {entityToken: cp.planar_entityTwo})
            WITH cp, planarEntityOne, planarEntityTwo
            WHERE planarEntityOne IS NOT NULL AND planarEntityTwo IS NOT NULL
            MERGE (cp)-[:USES {type: 'midplane',
                entity: 'one'}]->(planarEntityOne)
            MERGE (cp)-[:USES {type: 'midplane',
                entity: 'two'}]->(planarEntityTwo)
            RETURN cp.entityToken AS plane_id,
                planarEntityOne.entityToken AS planar_entityOne_id,
                planarEntityTwo.entityToken AS planar_entityTwo_id
            """,
            # offset
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'Offset'})
            OPTIONAL MATCH (planarEntity {entityToken: cp.planar_entity})
            WITH cp, planarEntity
            WHERE planarEntity IS NOT NULL
            MERGE (cp)-[:USES {type: 'offset',
                entity: 'planar'}]->(planarEntity)
            RETURN cp.entityToken AS plane_id,
                planarEntity.entityToken AS planar_entity_id
            """,
            # tangent_at_point
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'TangentAtPoint'})
            OPTIONAL MATCH (tangentFace {entityToken: cp.tangent_face}),
                        (pointEntity {entityToken: cp.point_entity})
            WITH cp, tangentFace, pointEntity
            WHERE tangentFace IS NOT NULL AND pointEntity IS NOT NULL
            MERGE (cp)-[:USES {type: 'tangent_at_point',
                entity: 'tangent_face'}]->(tangentFace)
            MERGE (cp)-[:USES {type: 'tangent_at_point',
                entity: 'point'}]->(pointEntity)
            RETURN cp.entityToken AS plane_id,
                tangentFace.entityToken AS tangent_face_id,
                pointEntity.entityToken AS point_entity_id
            """,
            # tangent
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'Tangent'})
            OPTIONAL MATCH (tangentFace {entityToken: cp.tangent_face}),
                        (planarEntity {entityToken: cp.planar_entity})
            WITH cp, tangentFace, planarEntity
            WHERE tangentFace IS NOT NULL AND planarEntity IS NOT NULL
            MERGE (cp)-[:USES {type: 'tangent',
                entity: 'tangent_face'}]->(tangentFace)
            MERGE (cp)-[:USES {type: 'tangent',
                entity: 'planar'}]->(planarEntity)
            RETURN cp.entityToken AS plane_id,
                tangentFace.entityToken AS tangent_face_id,
                planarEntity.entityToken AS planar_entity_id
            """,
            # three_points
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'ThreePoints'})
            OPTIONAL MATCH (pointEntityOne {entityToken: cp.point_entityOne}),
                        (pointEntityTwo {entityToken: cp.point_entityTwo}),
                        (pointEntityThree {entityToken: cp.point_entity_three})
            WITH cp, pointEntityOne, pointEntityTwo, pointEntityThree
            WHERE pointEntityOne IS NOT NULL AND pointEntityTwo IS NOT NULL \
                AND pointEntityThree IS NOT NULL
            MERGE (cp)-[:USES {type: 'three_points',
                entity: 'one'}]->(pointEntityOne)
            MERGE (cp)-[:USES {type: 'three_points',
                entity: 'two'}]->(pointEntityTwo)
            MERGE (cp)-[:USES {type: 'three_points',
                entity: 'three'}]->(pointEntityThree)
            RETURN cp.entityToken AS plane_id,
                pointEntityOne.entityToken AS point_entityOne_id,
                pointEntityTwo.entityToken AS point_entityTwo_id,
                pointEntityThree.entityToken AS point_entity_three_id
            """,
            # two_edges
            """
            MATCH (cp:`ConstructionPlane` {definition_type: 'TwoEdges'})
            OPTIONAL MATCH (linearEntityOne {entityToken:cp.linear_entityOne}),
                        (linearEntityTwo {entityToken: cp.linear_entityTwo})
            WITH cp, linearEntityOne, linearEntityTwo
            WHERE linearEntityOne IS NOT NULL AND linearEntityTwo IS NOT NULL
            MERGE (cp)-[:USES {type: 'two_edges',
                entity: 'one'}]->(linearEntityOne)
            MERGE (cp)-[:USES {type: 'two_edges',
                entity: 'two'}]->(linearEntityTwo)
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
            MERGE (f)-[:USES {type: 'axis'}]->(a)
            RETURN f.entityToken AS feature_id, f.axisToken AS axis_id
            """,
            # participant_body_relationships
            r"""
            MATCH (f)
            WHERE f.participantBodies IS NOT NULL
            UNWIND f.participantBodies AS body_token
            OPTIONAL MATCH (b {entityToken: body_token})
            WITH f, b WHERE b IS NOT NULL
            MERGE (f)-[:USES {type: 'participant_body'}]->(b)
            RETURN f.entityToken AS feature_id,
                collect(b.entityToken) AS participant_body_ids
            """,
            # extentOne_relationships
            r"""
            MATCH (f)
            WHERE f.extentOne_object_id IS NOT NULL
            OPTIONAL MATCH (e1 {entityToken: f.extentOne_object_id})
            MERGE (f)-[:USES {type: 'extent', order: 'one'}]->(e1)
            RETURN f.entityToken AS feature_id,
                f.extentOne_object_id AS extentOne_id
            """,
            # extentTwo_relationships
            r"""
            MATCH (f)
            WHERE f.extentTwo_object_id IS NOT NULL
            OPTIONAL MATCH (e2 {entityToken: f.extentTwo_object_id})
            MERGE (f)-[:USES {type: 'extent', order: 'two'}]->(e2)
            RETURN f.entityToken AS feature_id,
                f.extentTwo_object_id AS extentTwo_id
            """,
        ]

        results = []
        self.logger.info(
            'Linking features to axes, participant bodies, and extents')
        for query in queries:
            results.extend(execute_query(query))
        return results

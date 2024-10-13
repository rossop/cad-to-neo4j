"""
Profile Relationships Transformer

This module provides the transformation logic for profile relationships.

Classes:
    - ProfileTransformer: A class to handle profile-based transformations.
"""
from ..base_transformer import BaseTransformer
from ....utils.cypher_utils import helper_cypher_error


class ProfileTransformer(BaseTransformer):
    """
    ProfileTransformer

    A class to handle profile-based transformations.

    Methods:
        transform(execute_query): Runs all profile-related transformation
        methods.
    """
    def transform(self, execute_query):
        """
        Runs all profile-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_profile_loops_relationships'] =\
            self.create_profile_loops_relationships(execute_query)
        results['create_profile_curves_relationships'] =\
            self.create_profile_curves_relationships(execute_query)
        results['link_profile_curves_to_sketch_entities'] =\
            self.link_profile_curves_to_sketch_entities(execute_query)
        return results

    @helper_cypher_error
    def create_profile_loops_relationships(self, execute_query):
        """
        Creates relationships between profiles and their loops.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        self.logger.info(
            "Creating relationships between profiles and profile loops")
        query = """
            MATCH (p:Profile)
            WHERE p.profileLoops IS NOT NULL
            UNWIND p.profileLoops as profileLoopId
            MATCH (pl) WHERE pl.tempId = profileLoopId
            MERGE (p) -[:CONTAINS]->(pl)
            RETURN pl, p
        """
        return execute_query(query)

    @helper_cypher_error
    def create_profile_curves_relationships(self, execute_query):
        """
        Creates relationships between profile loops and their curves.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        self.logger.info(
            "Creating relationships between profile loops and profile curves")
        query = """
            MATCH (pl:ProfileLoop)
            WHERE pl.profileCurves IS NOT NULL
            UNWIND pl.profileCurves as pc_id
            MATCH (pc) WHERE pc.tempId = pc_id
            MERGE (pl) -[:CONTAINS]->(pc)
            RETURN pl, pc
        """
        return execute_query(query)

    @helper_cypher_error
    def link_profile_curves_to_sketch_entities(self, execute_query):
        """
        Links profile curves to their defining sketch entities.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        self.logger.info("Linking profile curves to sketch entities")
        query = """
            MATCH (sc:ProfileCurve)
            WHERE sc.sketchEntity IS NOT NULL
            MATCH (se)
            WHERE se.entityToken = sc.sketchEntity
            MERGE (sc)-[:DEFINED_BY]->(se)
            RETURN sc, se
        """
        return execute_query(query)

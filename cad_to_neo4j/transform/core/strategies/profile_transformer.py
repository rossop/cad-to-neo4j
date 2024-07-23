"""
Profile Relationships Transformer

This module provides the transformation logic for profile relationships.

Classes:
    - ProfileTransformer: A class to handle profile-based transformations.
"""

import traceback
from ..base_transformer import BaseTransformer

class ProfileTransformer(BaseTransformer):
    """
    ProfileTransformer

    A class to handle profile-based transformations.

    Methods:
        transform(execute_query): Runs all profile-related transformation methods.
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
        results['create_profile_loops_relationships'] = self.create_profile_loops_relationships(execute_query)
        results['create_profile_curves_relationships'] = self.create_profile_curves_relationships(execute_query)
        results['link_profile_curves_to_sketch_entities'] = self.link_profile_curves_to_sketch_entities(execute_query)
        return results

    def create_profile_loops_relationships(self, execute_query):
        """
        Creates relationships between profiles and their loops.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        self.logger.info("Creating relationships between profiles and profile loops")
        query = """
            MATCH (p:Profile)
            WHERE p.profileLoops IS NOT NULL
            UNWIND p.profileLoops as profileLoopId
            MATCH (pl) WHERE pl.tempId = profileLoopId
            MERGE (p) -[:CONTAINS]->(pl)
            RETURN pl, p
        """
        try:
            return execute_query(query)
        except Exception as e:
            self.logger.error(f"Error creating profile loops relationships: {e}\n{traceback.format_exc()}")
            return []

    def create_profile_curves_relationships(self, execute_query):
        """
        Creates relationships between profile loops and their curves.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        self.logger.info("Creating relationships between profile loops and profile curves")
        query = """
            MATCH (pl:ProfileLoop)
            WHERE pl.profileCurves IS NOT NULL
            UNWIND pl.profileCurves as pc_id
            MATCH (pc) WHERE pc.tempId = pc_id
            MERGE (pl) -[:CONTAINS]->(pc)
            RETURN pl, pc
        """
        try:
            return execute_query(query)
        except Exception as e:
            self.logger.error(f"Error creating profile curves relationships: {e}\n{traceback.format_exc()}")
            return []

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
        try:
            return execute_query(query)
        except Exception as e:
            self.logger.error(f"Error linking profile curves to sketch entities: {e}\n{traceback.format_exc()}")
            return []

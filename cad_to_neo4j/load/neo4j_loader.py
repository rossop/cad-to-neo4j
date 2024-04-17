"""
Neo4j Loader Module

This module provides functions to load CAD data into a Neo4j graph database.

Functions:
    - create_nodes: Creates multiple nodes in the Neo4j database.
    - create_relationships: Creates multiple relationships between nodes in the Neo4j database.
    - load_data: Loads extracted data into the Neo4j database.
"""

from neo4j import GraphDatabase
import os
from typing import Dict, List

__all__ = ['Neo4jLoader', 'create_nodes', 'create_relationships', 'load_data']

class Neo4jLoader:

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_nodes(self, tx, nodes: List[Dict]):
        """Creates multiple nodes in the Neo4j database in a batch.

        Args:
            tx: The transaction object.
            nodes (list): List of node dictionaries.
        """
        query = """
        UNWIND $nodes AS node
        CREATE (n: {type}) SET n = node.properties
        """
        tx.run(query, nodes=nodes)

    def create_relationships(self, tx, relationships: List[Dict]):
        """Creates multiple relationships in the Neo4j database in a batch.

        Args:
            tx: The transaction object.
            relationships (list): List of relationship dictionaries.
        """
        query = """
        UNWIND $relationships AS rel
        MATCH (a {entityToken: rel.from_id}), (b {entityToken: rel.to_id})
        CREATE (a)-[r:{rel_type}]->(b)
        """
        tx.run(query, relationships=relationships)

    def load_data(self, data: List[Dict]):
        """Loads extracted data into the Neo4j database.

        Args:
            data (list): The extracted data.
        """
        nodes = [{"type": element['type'], "properties": element} for element in data]

        # Create nodes in batches
        batch_size = 1000
        with self.driver.session() as session:
            for i in range(0, len(nodes), batch_size):
                session.write_transaction(self.create_nodes, nodes[i:i + batch_size])

            # Create NEXT_ON_TIMELINE relationships in batches
            relationships = []
            for i in range(len(data) - 1):
                relationships.append({
                    "from_id": data[i]['id_token'],
                    "to_id": data[i + 1]['id_token'],
                    "rel_type": "NEXT_ON_TIMELINE"
                })

            for i in range(0, len(relationships), batch_size):
                session.write_transaction(self.create_relationships, relationships[i:i + batch_size])

            # Assuming BUILT_ON relationship logic is added later
            # for now, this relationship is not implemented

# Usage example
if __name__ == "__main__":
    loader = Neo4jLoader(uri, user, password)
    # Example data to load
    data = [
        {'type': 'Sketch', 'id_token': 'id1', 'name': 'Sketch1'},
        {'type': 'Feature', 'id_token': 'id2', 'name': 'Extrude1'},
        # Add more data as needed
    ]
    loader.load_data(data)
    loader.close()

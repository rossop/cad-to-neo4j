"""
JSON Output Utility Module

This module provides a utility class for outputting nodes to a JSON file.

Classes:
    - JSONOutputUtility: A class with a static method to save a dictionary of nodes to a specified JSON file.

Functions:
    - output_nodes_to_json: Outputs the nodes dictionary to a JSON file.

Usage:
    JSONOutputUtility.output_nodes_to_json(nodes, "output_nodes.json")
"""

import json
from typing import Dict, Any

__all__ = ['JSONOutputUtility']

class JSONOutputUtility:
    """
    Utility class for outputting nodes to a JSON file.

    This class provides a static method to save a dictionary of nodes to a specified JSON file.

    Methods:
        output_nodes_to_json(nodes, file_path): Outputs the nodes dictionary to a JSON file.
    """
    
    @staticmethod
    def output_nodes_to_json(nodes: Dict[str, Dict[str, Any]], file_path: str) -> None:
        """
        Outputs the nodes dictionary to a JSON file.

        Args:
            nodes (Dict[str, Dict[str, Any]]): The dictionary of nodes to be outputted.
            file_path (str): The path where the JSON file will be saved.

        Raises:
            IOError: If there is an issue with writing to the file.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(nodes, json_file, ensure_ascii=False, indent=4)
            print(f"Successfully wrote nodes to {file_path}")
        except IOError as e:
            print(f"Error writing nodes to JSON file: {e}")

# Usage example
if __name__ == "__main__":
    nodes_example = {
        "node1": {"property1": "value1", "property2": "value2"},
        "node2": {"property1": "value3", "property2": "value4"},
    }
    JSONOutputUtility.output_nodes_to_json(nodes_example, "output_nodes.json")

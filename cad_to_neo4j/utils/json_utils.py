"""
JSON Output Utility Module

This module provides a utility class for outputting nodes to a JSON file.

Classes:
    - JSONOutputUtility: A class with a static method to save a dictionary of nodes to a specified JSON file.

Functions:
    - output_nodes_to_json: Outputs the nodes dictionary to a JSON file.

Usage:
    JSONOutputUtility.output_nodes_to_json(nodes, "output_nodes.json", logger=my_logger)
"""

import json
import os
import logging
from typing import Dict, Any, Optional

__all__ = ['JSONOutputUtility']

class JSONOutputUtility:
    """
    Utility class for outputting nodes to a JSON file.

    This class provides a static method to save a dictionary of nodes to a specified JSON file.

    Methods:
        output_nodes_to_json(nodes, file_path, logger): Outputs the nodes dictionary to a JSON file.
    """
    
    @staticmethod
    def output_nodes_to_json(nodes: Dict[str, Dict[str, Any]], file_path: str, logger: Optional[logging.Logger] = None) -> None:
        """
        Outputs the nodes dictionary to a JSON file.

        Args:
            nodes (Dict[str, Dict[str, Any]]): The dictionary of nodes to be outputted.
            file_path (str): The path where the JSON file will be saved.
            logger (logging.Logger, optional): The logger object for logging messages and errors. Defaults to None.

        Raises:
            IOError: If there is an issue with writing to the file.
        """
        if logger is None:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger('JSONOutputUtility')

        # Expand user directory if present in the file_path
        file_path = os.path.expanduser(file_path)

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(nodes, json_file, ensure_ascii=False, indent=4)
            logger.info(f"Successfully wrote nodes to {file_path}")
        except IOError as e:
            logger.error(f"Error writing nodes to {file_path}: {e}")
            if 'Read-only file system' in str(e):
                try:
                    fallback_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'output_nodes.json')
                    with open(fallback_path, 'w', encoding='utf-8') as json_file:
                        json.dump(nodes, json_file, ensure_ascii=False, indent=4)
                    logger.info(f"Successfully wrote nodes to fallback path {fallback_path}")
                except IOError as fallback_e:
                    logger.error(f"Error writing nodes to fallback path: {fallback_e}")

# Usage example
if __name__ == "__main__":
    nodes_example = {
        "node1": {"property1": "value1", "property2": "value2"},
        "node2": {"property1": "value3", "property2": "value4"},
    }
    JSONOutputUtility.output_nodes_to_json(nodes_example, '~/Desktop/output_nodes.json')
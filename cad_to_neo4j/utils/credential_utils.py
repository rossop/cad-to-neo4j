"""
Credentials Utilities Module

This module provides utilities for loading environment variables 
such as Neo4j credentials.

Functions:
    - load_credentials: Loads Neo4j credentials from a .env file.
"""

__all__ = ['load_credentials']

import os
from dotenv import load_dotenv

def load_credentials(dotenv_path: str = None) -> dict:
    """Loads Neo4j credentials from a .env file.

    Args:
        dotenv_path (str): The path to the .env file. Defaults to None.

    Returns:
        dict: A dictionary containing the Neo4j URI, user, and password.
    """
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path)
    else:
        load_dotenv()

    return {
        "NEO4J_URI": os.getenv('NEO4J_URI'),
        "NEO4J_USER": os.getenv('NEO4J_USER'),
        "NEO4J_PASSWORD": os.getenv('NEO4J_PASSWORD')
    }
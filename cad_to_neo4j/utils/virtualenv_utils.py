"""
Virtual Environment Utilities Module

This module provides functions to manage the inclusion and removal of 
virtual environment site-packages in the sys.path. It ensures that the 
Python environment can access the necessary packages installed in the 
virtual environment.

Functions:
    - add_virtualenv_to_path: Adds the virtual environment site-packages to sys.path.
    - remove_virtualenv_from_path: Removes the virtual environment site-packages from sys.path.
"""

import sys
import os

__all__ = ['add_virtualenv_to_path', 'remove_virtualenv_from_path']

SITE_PACKAGES_PATH = None

def add_virtualenv_to_path(venv_dir):
    """
    Adds the virtual environment site-packages to sys.path.

    Args:
        venv_dir (str): The directory of the virtual environment.

    Raises:
        EnvironmentError: If the operating system is not supported.
        FileNotFoundError: If the site-packages path does not exist.
    """
    global SITE_PACKAGES_PATH
    if sys.platform == "win32":
        venv_site_packages = os.path.join(venv_dir, 'Lib', 'site-packages')
    elif sys.platform == "darwin":
        venv_site_packages = os.path.join(venv_dir, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
    else:
        raise EnvironmentError("Unsupported operating system")

    if not os.path.exists(venv_site_packages):
        raise FileNotFoundError(f"Site-packages path does not exist: {venv_site_packages}")

    if venv_site_packages not in sys.path:
        sys.path.insert(0, venv_site_packages)  # Ensure it is the first path to be checked
        SITE_PACKAGES_PATH = venv_site_packages

def remove_virtualenv_from_path():
    """
    Removes the virtual environment site-packages from sys.path.
    """
    global SITE_PACKAGES_PATH
    if SITE_PACKAGES_PATH and SITE_PACKAGES_PATH in sys.path:
        sys.path.remove(SITE_PACKAGES_PATH)
        SITE_PACKAGES_PATH = None

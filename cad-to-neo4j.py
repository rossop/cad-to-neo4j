"""
# Author: Peter Rosso
# Description: This script is used to extract information regarding the Fusion 360
# environment to facilitate development. The script was inspired by Jorge_Jaramillo's answer on the Autodesk Community.
"""

import sys
import os
import adsk.core, adsk.fusion, adsk.cam, traceback
import logging
from typing import Union
import pkg_resources
from datetime import datetime
# Define the global variable for the added site-packages path
SITE_PACKAGES_PATH = None

def add_virtualenv_to_path(venv_dir):
    """Adds the virtual environment site-packages to sys.path."""
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

def remove_virtualenv_from_path(venv_dir):
    """Removes the virtual environment site-packages from sys.path."""
    global SITE_PACKAGES_PATH
    if SITE_PACKAGES_PATH and SITE_PACKAGES_PATH in sys.path:
        sys.path.remove(SITE_PACKAGES_PATH)
        SITE_PACKAGES_PATH = None

# Add the virtual environment to the Python path
VENV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fusion_venv')
add_virtualenv_to_path(VENV_DIR)

# Import dotenv after adding the virtual environment to the path
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Neo4j credentials
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

from .cad_to_neo4j.utils.logger_utils import Logger, log_function, console_handler, file_handler
from .cad_to_neo4j.load import Neo4jLoader
from .cad_to_neo4j.extract import extract_component_data, extract_data

def run(context):
    global Logger, console_handler, file_handler, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
    ui = None
    Loader = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the command palette
        text_palette = ui.palettes.itemById('TextCommands')
        if not text_palette:
            Logger.error("Couldn't get the Text Commands palette")
            return
    
        
        if Logger:
            Logger.info('Starting CAD extraction process')
        else:
            app.log('No Logger vailable')

        
        # Get the active document and design
        product = app.activeProduct
       
        design = adsk.fusion.Design.cast(product)
        if not design:
            Logger.error('No active Fusion design')
            return None
       
        # Initialise Neo4J Loader 
        with Neo4jLoader(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, Logger=Logger) as Loader:
            # Extract component data
            nodes, relationships = extract_component_data(design, Logger=Logger)
            
            # Load all nodes and relationships in batch
            Loader.load_data(nodes, relationships)

        Logger.info('CAD extraction process completed')

    except Exception as e:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}')
        Logger.error(f'Exception: {e}')
    finally:
        # Cleanup
        remove_virtualenv_from_path(VENV_DIR)
        for handler in Logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                text_palette.writeText(handler.stream.getvalue())
def stop(context):
    global Logger, console_handler, file_handler
    Logger.info("Stopping Script and cleaning up logger.")
    if Logger:
        Logger.removeHandler(console_handler)
        Logger.removeHandler(file_handler)
        Logger = None
    
    if console_handler:
        console_handler.close()
        console_handler = None
    
    if file_handler:
        file_handler.close()
        file_handler = None
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

from .cad_to_neo4j.utils.logger import Logger, log_function, console_handler, file_handler
from .cad_to_neo4j.extract import get_extractor
from .cad_to_neo4j.load.neo4j_loader import Neo4jLoader

@log_function
def extract_data(element: Union[adsk.fusion.Sketch, adsk.fusion.Feature]):
    try:
        Logger.info(f"Processing element: {element.classType()}")
        Extractor = get_extractor(element)
        extracted_info = Extractor.extract_all_info()
        return {
            "type": element.classType(),
            "properties": extracted_info
        }
    except Exception as e:
        Logger.error(f"Error in extract_data: {str(e)}")
        return None

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

        # Log initial Python environment details
        app.log(" "*20) 
        app.log("_"*20) 
        # datetime object containing current date and time
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        app.log(f'{dt_string}')

        app.log(f'sys version_info: {sys.version_info}')
        app.log(f'sys executable: {sys.executable}')
        app.log(f'sys path: {len(sys.path)}')
        
        # Log installed packages
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        app.log(f'Installed libraries: {installed_packages}')
        
        if Logger:
            Logger.info('Starting CAD extraction process')
        else:
            app.info('No Logger vailable')

        
        # Get the active document and design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            Logger.error('No active Fusion design')
            return None
       
        # Initialise Neo4J loader
        nodes = []
        relationships = []
        with Neo4jLoader(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, Logger=Logger) as Loader:
            # Process timeline
            timeline = design.timeline
            for i in range(timeline.count):
                extracted_info = extract_data(timeline.item(i).entity)
                if extracted_info:
                    nodes.append(extracted_info)
                    if i > 0:
                        relationships.append({
                            "from_id": nodes[i-1]['properties']['id_token'],
                            "to_id": nodes[i]['properties']['id_token'],
                            "rel_type": "NEXT_ON_TIMELINE"
                        })

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
    
    print("Script stopped and logger cleaned up.")


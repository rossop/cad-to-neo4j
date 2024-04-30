"""
# Author: Peter Rosso
# Description: This script is used to extract information regarding the Fusion 360
# environment to facilitate development. 
"""

import sys
import os
import adsk.core, adsk.fusion, adsk.cam, traceback
import logging

# Import and run the virtual environment setup
from .setup_environment import add_virtualenv_to_path, remove_virtualenv_from_path

from .cad_to_neo4j.utils.credential_utils import load_credentials
# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
credentials = load_credentials(dotenv_path=dotenv_path)

# Neo4j credentials
NEO4J_URI = credentials["NEO4J_URI"]
NEO4J_USER = credentials["NEO4J_USER"]
NEO4J_PASSWORD = credentials["NEO4J_PASSWORD"]

from .cad_to_neo4j.utils.logger_utils import Logger, console_handler, file_handler # TODO setup logger here
from .cad_to_neo4j.extract import extract_component_data
from .cad_to_neo4j.load import Neo4jLoader
from .cad_to_neo4j.tranform import Neo4jTransformer

def run(context):
    global app, Logger, console_handler, file_handler, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
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
            nodes, relationships = extract_component_data(design, Logger=Logger) # TODO turn into extractor object
            
            # Load all nodes and relationships in batch
            Loader.load_data(nodes, relationships)

        with Neo4jTransformer(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, Logger=Logger) as Transformer:
            # Transform graph data
            _ = Transformer.execute()

        Logger.info('CAD extraction process completed')

    except Exception as e:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}')
        Logger.error(f'Exception: {e}')
    finally:
        # Cleanup
        if Logger:
            for handler in Logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    text_palette.writeText(handler.stream.getvalue())


def stop(context):
    global Logger, console_handler, file_handler, app
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

    try:
        remove_virtualenv_from_path()
    except Exception as e:
            app.log(f'Exception: {e}')

    if app:
        app.log("Script stopped and logger cleaned up.")
        app = None
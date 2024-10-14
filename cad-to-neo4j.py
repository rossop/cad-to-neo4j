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

from .cad_to_neo4j.utils.logger_utils import logger_utility
from .cad_to_neo4j.extract import ExtractorOrchestrator
from .cad_to_neo4j.load import Neo4jLoader
from .cad_to_neo4j.transform import Neo4jTransformerOrchestrator

def run(context):
    global app, logger_utility, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
    ui = None
    Loader = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the command palette
        text_palette = ui.palettes.itemById('TextCommands')
        if not text_palette:
            logger_utility.logger.error("Couldn't get the Text Commands palette")
            return


        if logger_utility.logger:
            logger_utility.logger.info('Starting CAD extraction process')
        else:
            app.log('No Logger vailable')


        # Get the active document and design
        product = app.activeProduct

        design = adsk.fusion.Design.cast(product)
        if not design:
            logger_utility.logger.error('No active Fusion design')
            return None

        # Initialise Neo4J Loader
        with Neo4jLoader(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, logger=logger_utility.logger) as Loader:

            # Clear Graph:
            Loader.clear()
            # Initialize the orchestrator
            Orchestrator = ExtractorOrchestrator(design, logger_utility.logger)

            # Extract component data
            nodes = Orchestrator.extract_timeline_based_data()

            # Load all nodes and relationships in batch
            Loader.load_data(nodes, []) # TODO remove relationships

        with Neo4jTransformerOrchestrator(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, logger=logger_utility.logger) as Transformer:
            # Transform graph data
            _ = Transformer.execute()

        logger_utility.logger.info('CAD extraction process completed')

    except Exception as e:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}')
        logger_utility.logger.error(f'Exception: {e}')
    finally:
        # Cleanup
        if logger_utility.logger:
            for handler in logger_utility.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    text_palette.writeText(handler.stream.getvalue())


def stop(context):
    global logger_utility, app
    logger_utility.logger.info("Stopping Script and cleaning up logger.")

    # Clean up logger
    if logger_utility:
        del logger_utility

    try:
        remove_virtualenv_from_path()
    except Exception as e:
            app.log(f'Exception: {e}')

    if app:
        app.log("Script stopped and logger cleaned up.")
        app = None
import sys
import os

# Add the cad_to_neo4j directory to the Python path
print(os.path.dirname(__file__))

import adsk.core, adsk.fusion, adsk.cam, traceback
import logging

from .cad_to_neo4j.utils.logger import Logger, log_function, console_handler, file_handler, inspect_object
from .cad_to_neo4j.extract.base_extractor import BaseExtractor


@log_function
def do_stuff(element):
    try:
        Logger.info(f"Processing element: {element.classType()}")
        Extractor = BaseExtractor(element)
        info = Extractor.extract_basic_info()
        Logger.debug(f'{info}')
        # inspect_object(element)

    except Exception as e:
        Logger.error(f"Error in do_stuff: {str(e)}")

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Get the command palette
        text_palette = ui.palettes.itemById('TextCommands')
        if not text_palette:
            Logger.error("Couldn't get the Text Commands palette")
            return

        # Make sure the palette is visible
        if not text_palette.isVisible:
            text_palette.isVisible = True

        Logger.info('Starting CAD extraction process')

        # Get the active document and design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            Logger.error('No active Fusion design')
            return

        # Get the root component of the active design
        root_comp = design.rootComponent
        
        # Process timeline
        timeline = design.timeline
        for i in range(timeline.count):
            do_stuff(timeline.item(i).entity)

        Logger.info('CAD extraction process completed')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    finally:
        # Display all logged messages in the Text Commands palette
        for handler in Logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                text_palette.writeText(handler.stream.getvalue())


def stop(context):
    global Logger, console_handler, file_handler
    Logger.removeHandler(console_handler)
    Logger.removeHandler(file_handler)
    console_handler.close()
    file_handler.close()
    Logger = None
    console_handler = None
    file_handler = None
    print("Script stopped and logger cleaned up.")
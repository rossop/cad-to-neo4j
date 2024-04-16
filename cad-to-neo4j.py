import sys
import os

# Add the cad_to_neo4j directory to the Python path
print(os.path.dirname(__file__))

import adsk.core, adsk.fusion, adsk.cam, traceback
import logging


from .cad_to_neo4j.utils.logger import Logger, log_function, console_handler, file_handler  # Import logger, decorator, and handlers



# Inspect Object
def inspect_object(obj):
    """Helper function to inspect and log object properties and methods"""
    Logger.debug(f"_______________________________")
    class_name = obj.__class__.__name__
    Logger.debug(f"Inspecting {class_name} object:")
    
    for attr_name in dir(obj):
        if not attr_name.startswith('__'):  # Skip built-in attributes
            try:
                attr_value = getattr(obj, attr_name)
                if callable(attr_value):
                    Logger.debug(f"  Method: {attr_name}")
                else:
                    Logger.debug(f"  Property: {attr_name} = {attr_value}")
            except:
                Logger.debug(f"  Unable to access: {attr_name}")

@log_function
def do_stuff(element):
    try:
        Logger.info(f"Processing element: {element.classType()}")
        inspect_object(element)
        # Add more specific logging as needed
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


# def stop(context):
#     global logger, console_handler
#     logger.removeHandler(console_handler)
#     console_handler.close()
#     logger = None
#     console_handler = None
#     print("Script stopped and logger cleaned up.")

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
"""
Extractor Factory Module

This module provides a factory function to get the appropriate extractor
based on the type of CAD element. It also provides a function to extract 
data from components (including elements contained withing it, such as 
sketches, featurs, and BRep bodies.

Functions:
    - get_extractor: Returns the appropriate extractor for the given 
      element.
    - extract_data: Extracts data from the given element using the 
      appropriate extractor.
    - extract_component_data: Extracts data from components, sketches, 
      features, and BRep bodies.
"""
import logging
from typing import Tuple, List, Dict

from adsk.core import Base
from adsk.fusion import Sketch, Feature, BRepBody, Component, Design # TODO standardise adsk impors
from .base_extractor import BaseExtractor
from .sketch_extractor import SketchExtractor
from .extrude_feature_extractor import ExtrudeFeatureExtractor
from .brep_extractor import BRepExtractor
from ..utils.logger_utils import Logger

__all__ = ['get_extractor', 'extract_data', 'extract_component_data']

EXTRACTORS = {
    'adsk::fusion::Sketch': SketchExtractor,
    'adsk::fusion::ExtrudeFeature': ExtrudeFeatureExtractor, 
    'adsk::fusion::BRepBody': BRepExtractor, 
}
# TODO generalise for different features

def get_extractor(element: Base) -> BaseExtractor:
    """Get the appropriate extractor for the given CAD element.

    Args:
        element (Base): The CAD element.

    Returns:
        BaseExtractor: The appropriate extractor for the element.
    """
    extractor_class = EXTRACTORS.get(element.objectType, BaseExtractor)
    return extractor_class(element)


def extract_data(element: Base) -> dict:
    """Extracts data from the given element using the appropriate extractor.

    Args:
        element (Base): The CAD element.

    Returns:
        dict: The extracted data.
    """
    try:
        Extractor = get_extractor(element)
        extracted_info = Extractor.extract_info()
        return {
            "type": element.classType(),
            "properties": extracted_info
        }
    except Exception as e:
        Logger.error(f"Error in extract_data: {str(e)}")
        return None

def extract_component_data(design: Design, 
                           Logger: logging.Logger = None) -> Tuple[List[Dict], List[Dict]]:
    """
    Extracs data from the components, and their children sketches, features and
    BRep bodies in the design.

    Args:
        desing: The Fusion360 design object.
        Logger: The logger object for logging messages and errors.

    Returns:
        tuple: A tuple containing the list of nodes and relationships.
    """
    nodes = []
    relationships = [] # TODO turn into a set to avoid repetition
    processed_ids = set()  # Set to avoid duplication of nodes
    processed_relationships = set()  # Set to avoid duplication of relationships

    def add_relationship(from_id, to_id, rel_type):
        """Helper function to add a relationship and avoid duplication."""
        if (from_id, to_id, rel_type) not in processed_relationships:
            relationships.append({
                "from_id": from_id,
                "to_id": to_id,
                "rel_type": rel_type
            })
            processed_relationships.add((from_id, to_id, rel_type))


    def extract_and_append(entity, parent_id, rel_type):
        """Helper function to extract data and append nodes and relationships."""
        try:
            extracted_info = extract_data(entity)
            if extracted_info:
                entity_id = extracted_info['properties']['id_token']
                if entity_id not in processed_ids:
                    nodes.append(extracted_info)
                    processed_ids.add(entity_id)
                add_relationship(parent_id, entity_id, rel_type)
                return entity_id    
        except Exception as e:
            if Logger:
                Logger.error(f"Error extracting and appending data for {entity}: {str(e)}")
                Logger.error(f"Extracted info: {extracted_info}")
        return None
    
    def extract_brep_entity_data(brep_entity, parent_id):
        """Helper function to extract and append BRep entities."""
        entity_id = extract_and_append(brep_entity, parent_id, "CONTAINS")
        if not entity_id:
            return

        # Extract and append faces, edges, and vertices
        for face in brep_entity.faces:
            face_id = extract_and_append(face, entity_id, "CONTAINS")
            for edge in face.edges:
                edge_id = extract_and_append(edge, face_id, "CONTAINS")
                for vertex in [edge.startVertex, edge.endVertex]:
                    _ = extract_and_append(vertex, edge_id, "CONTAINS")

                # Establish ADJACENT relationships for edges
                # TODO avoid self adjacency
                for adjacent_edge in edge.tangentiallyConnectedEdges:
                    _ = extract_and_append(adjacent_edge, edge_id, "ADJACENT")

            # Establish ADJACENT relationships for faces
            # TODO understnad why there are no adjacency between faces
            for adjacent_face in face.tangentiallyConnectedFaces:
                _ = extract_and_append(adjacent_face, face_id, "ADJACENT")

    def extract_sketch_profiles(sketch, parent_id):
        """Helper function to extract profiles from a sketch and link them."""
        sketch_id = extract_and_append(sketch, parent_id, "CONTAINS")
        if not sketch_id:
            return
        
        for profile in sketch.profiles:
            profile_id = extract_and_append(profile, sketch_id, "CONTAINS")
            if profile_id:
                add_relationship(sketch_id, profile_id, "CONTAINS")

    comp = design.rootComponent
    if comp:
        Logger.info('Starting component Extraction')
        Logger.info(f'Extracting component: {comp.name}')

        # Extract compnent node
        component_info = extract_data(comp)
        if component_info:
            nodes.append(component_info)
            component_id = component_info['properties']['id_token']

        # Extract Sketches
        for sketch in comp.sketches:
            extract_sketch_profiles(sketch, component_id)

        # Extract Features 
        for feat in comp.features:
            feature_id = extract_and_append(feat, component_id, "CONTAINS")

            # Extraact BRep bodies generated by this feature
            if feature_id and hasattr(feat, 'bodies'):
                for body in feat.bodies:
                    extract_brep_entity_data(body, feature_id)

        for body in comp.bRepBodies:
            _ = extract_and_append(body, component_id, "CONTAINS")

    return nodes, relationships
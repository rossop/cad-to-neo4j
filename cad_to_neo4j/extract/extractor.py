"""
Extractor Orchestrator Module

This module provides an orchestrator class to manage the extraction of
data from CAD elements in a Fusion 360 design. It concludes functions 
to get the approriate extractor based on the type of CAD element and to
extract data from components, sketches, features and BRep bodies in a
structured manner.

Classes:
    - ExtractorOrchestractor: Manages the extraction process, coordinating
        between various extractors and ensuring data is collected in a
        timeline-based order.

Functions:
    - get_extractor: Returns the appropriate extractor for the given 
      element.
    - extract_data: Extracts data from the given element using the 
      appropriate extractor.

Usage:
    orchestrator = ExtractOrchestrator(design)
    nodes, relationships = orchestrator.extract_component_data()
    timeline_nodes, timeline_relationships = orchestrator.extract_timeline_based_data()
"""
import logging
from typing import Optional, Tuple, Any, List, Dict, Set
from adsk.core import Base
from adsk.fusion import Design, Component,  Feature, Sketch, BRepBody
import traceback

from .base_extractor import BaseExtractor
from .extractors import EXTRACTORS, ENTITY_MAP


__all__ = ['ExtractorOrchestrator']

class ExtractorOrchestrator(object):
    """
    Manages the extraction process, coordinating between various extractors 
    and ensuring data is collected in a timeline-based order.

    Args:
        design (Design): The Fusion 360 design object.
        logger (logging.Logger, optional): The logger object for logging messages and errors.
    """
    # TODO Refactor methods
    def __init__(self, design: Design, logger: logging.Logger = None):
        self.design = design
        self.logger = logger
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.processed_relationships = set()
        self.timeline_index: str = 0

    def get_extractor(self, element: Base) -> BaseExtractor:
        """Get the appropriate extractor for the given CAD element.

        Args:
            element (Base): The CAD element.

        Returns:
            BaseExtractor: The appropriate extractor for the element.
        """
        extractor_class = EXTRACTORS.get(element.objectType, BaseExtractor)
        return extractor_class(element)

    def extract_data(self, element: Base) -> Optional[dict]:
        """
        Extracts data from the given element using the appropriate extractor 
        and stores it.

        Args:
            element (Base): The CAD element.

        Returns:
            dict: The extracted data.
        """
        try:
            Extractor = self.get_extractor(element)
            extracted_info = Extractor.extract_info()
            if extracted_info:
                entity_id = extracted_info['id_token']
                if entity_id not in self.nodes:
                    self.nodes[entity_id] = extracted_info
        except Exception as e:
            self.logger.error(f"""
                              Error in extract_data: {str(e)}\n
                              Failed:\n{traceback.format_exc()}
                            """)
    
    # def extract_brep_entity_data(self, brep_entity: Base) -> None:
    #     """
    #     Helper function to extract and append BRep entities.

    #     Args:
    #         brep_entity (Base): The BRep entity to extract data from.
    #         parent_id (str): The ID of the parent node.
    #         timeline_index (int, optional): The index of the timeline. Defaults to None.
    #     """
    #     # TODO add try and catch 
    #     self.extract_data(brep_entity)

    #     for face in brep_entity.faces:
    #         self.extract_data(face)

    #     for edge in brep_entity.edges:
    #         self.extract_data(edge)

    #     for vertex in brep_entity.vertices:
    #         self.extract_data(vertex)

    def extract_sketch_entities(self, sketch: Sketch) -> None:
        """
        Helper function to extract entities from a sketch and link them.

        Args:
            sketch (Sketch): The sketch to extract entities from.
        """
        # TODO add try and catch
        for profile in sketch.profiles:
            self.extract_data(profile)
            
        for point in sketch.sketchPoints:
            self.extract_data(point)
        
        for curve in sketch.sketchCurves:
            self.extract_data(curve)

        for dimension in sketch.sketchDimensions:
            self.extract_data(dimension)

        for constraint in sketch.geometricConstraints:
            self.extract_data(constraint)

    def extract_component_data(self) -> None:
        """
        Extracts data from the components, and their children sketches, features
        and BRep bodies in the design.

        Returns:
            tuple: A tuple containing the list of nodes and relationships.
        """
        comp = self.design.rootComponent
        if comp:
            self.logger.info('Starting component Extraction')
            self.logger.info(f'Extracting component: {comp.name}')

        return None

    def _get_current_brep_entities(self, comp: Component) -> None:
        """
        Get the current BRep entities (faces, edges, vertices) of the component.
        
        Args:
            comp (Component): The Fusion 360 component.

        Returns:
            tuple: A tuple containing sets of current face, edge, and vertex tokens.
        """
        # TODO avoid repeating the body loop and share it across them
        self.current_faces = {face.entityToken for body in comp.bRepBodies for face in body.faces}
        self.current_edges = {edge.entityToken for body in comp.bRepBodies for edge in body.edges}
        self.current_vertices = {vertex.entityToken for body in comp.bRepBodies for vertex in body.vertices}

    def _process_new_entities(self, new_entities: Set[str], entity_type: str, comp: Component):
        """
        Process new BRep entities (faces, edges, vertices) and add them to the extraction nodes and relationships.

        Args:
            new_entities (Set[str]): Set of new entity tokens.
            entity_type (str): Type of the BRep entity ('face', 'edge', 'vertex').
            comp (Component): The Fusion 360 component.
            feature_id (str): The ID of the feature.
            index (int): The timeline index.
        """
        # TODO is there a mroe efficient way either way using 
        if entity_type not in ENTITY_MAP:
            return None

        entity_attr, extractor_class = ENTITY_MAP[entity_type] # remove and just use entity_type

        for token in new_entities: # TODO change new entities to dictionary and use entity type as key
            entity = next((e for body in comp.bRepBodies for e in getattr(body, entity_attr) if e.entityToken == token), None)
            self.extract_data(entity)

    def _extract_feature(self, entity: Feature, comp: Component):
        """
        Extract data from a feature entity and process its BRep entities.

        Args:
            entity (Feature): The Fusion 360 feature entity.
            comp (Component): The Fusion 360 component.
            index (int): The timeline index.
            component_id (str): The ID of the component.
            self.previous_faces (Set[str]): Set of previous face tokens.
            self.previous_edges (Set[str]): Set of previous edge tokens.
            self.previous_vertices (Set[str]): Set of previous vertex tokens.
        """
        self.logger.info(f'Extracting feature at timeline index {self.timeline_index}: {entity.name}')
        self.extract_data(entity)
        if True:
            self._get_current_brep_entities(comp)
            self.new_faces = self.current_faces - self.previous_faces
            self.new_edges = self.current_edges - self.previous_edges
            self.new_vertices = self.current_vertices - self.previous_vertices

            self._process_new_entities(self.new_faces, 'face', comp)
            self._process_new_entities(self.new_edges, 'edge', comp)
            self._process_new_entities(self.new_vertices, 'vertex', comp)

    def _extract_sketch(self, sketchEntity: Sketch):
        """
        Extract data from a sketch entity and the contained entities.

        Args:
            sketchEntity (Sketch): The Fusion 360 sketch entity.
        """
        self.logger.info(f'Extracting sketch at timeline index {self.timeline_index}: {sketchEntity.name}')
        self.extract_data(sketchEntity)
        self.extract_sketch_entities(sketchEntity)

    def extract_brep_entities(self, comp: Component) -> None:
        """
        Extract final BRep entities and establish relationships.

        Args:
            comp (Component): The Fusion 360 component.
        """
        self.logger.info('Extracting final BRep entities and establishing relationships')

        for body in comp.bRepBodies:
            self.extract_data(body)

        for face in comp.faces:
            self.extract_data(face)

        for edge in comp.edges:
            self.extract_data(edge)

        for vertex in comp.bRepBodies:
            self.extract_data(vertex)


    def _extract_other_entity(self, entity: Base) -> None:
        """Extract data for other entity types."""
        self.extract_data(entity)

    def _extract_origin_construction_geometry(self, comp: Component) -> None:
        """
        Extracts construction planes and axes from the component.

        Args:
            comp (Component): The Fusion 360 component.
            component_id (str): The ID of the component node.
        """
        construction_planes = [
            comp.xYConstructionPlane,
            comp.xZConstructionPlane,
            comp.yZConstructionPlane
        ]

        construction_axes = [
            comp.xConstructionAxis,
            comp.yConstructionAxis,
            comp.zConstructionAxis
        ]

        origin = comp.originConstructionPoint

        for plane in construction_planes:
            self.extract_data(plane)

        for axis in construction_axes:
            self.extract_data(axis)

        self.extract_data(origin)

    def extract_timeline_based_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract data based on the timeline order.

        Returns:
            tuple: A tuple containing the list of nodes and relationships.
        """
        comp = self.design.rootComponent
        timeline = self.design.timeline

        self.previous_faces: Set[str] = set()
        self.previous_edges: Set[str] = set()
        self.previous_vertices: Set[str] = set()

        self.extract_data(comp)
        self._extract_origin_construction_geometry(comp)

        for index in range(timeline.count):
            timelineObject = timeline.item(index)
            entity = timelineObject.entity

            # Roll to current timeline
            self.logger.info(f'Rolling to timeline index {index}')
            timelineObject.rollTo(True)

            # Ensure the collections are updated after rolling the timeline
            self._get_current_brep_entities(comp)

            if entity:
                if isinstance(entity, Feature):
                    self._extract_feature(entity, comp)
                elif isinstance(entity, Sketch):
                    self._extract_sketch(entity)
                else:
                     self._extract_other_entity(entity)

                # Update previous sets
                self.previous_faces = self.current_faces.copy()
                self.previous_edges = self.current_edges.copy()
                self.previous_vertices = self.current_vertices.copy()

        return list(self.nodes.values())
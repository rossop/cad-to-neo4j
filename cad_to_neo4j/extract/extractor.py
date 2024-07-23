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
import copy

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
        self.timelineIndex: str = 0

    def get_extractor(self, element) -> BaseExtractor:
        """Get the appropriate extractor for the given CAD element.

        Args:
            element (Base): The CAD element.

        Returns:
            Extractor (BaseExtractor): The appropriate extractor for the element.
        """
        extractor_class = EXTRACTORS.get(element.objectType, BaseExtractor)
        return extractor_class(element)

    def extract_data(self, element) -> Optional[dict]:
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
                entity_id = extracted_info['entityToken']
                if entity_id not in self.nodes:
                    self.nodes[entity_id] = extracted_info
                else:
                    self.add_or_update(self.nodes[entity_id],extracted_info)
                    
        except Exception as e:
            self.logger.error(f"""
                              Error in extract_data: {str(e)}\n
                              Failed:\n{traceback.format_exc()}
                            """)
                
    def extract_nested_data(self, element, parent_id=None):
        """
        Extracts nested data from the given element using the appropriate extractor 
        and stores it.

        Args:
            element (Base): The CAD element.

        Returns:
            dict: The flattened data.
        """
        def contains_dict(lst):
            """
            Check if a list contains any dictionaries.
            
            Args:
                lst (list): The list to check.
            
            Returns:
                bool: True if any item in the list is a dictionary, False otherwise.
            """
            return any(isinstance(item, dict) for item in lst)

        def check_dict_values(d):
            """
            Check if any values in a dictionary are lists that contain dictionaries.
            
            Args:
                d (dict): The dictionary to check.
            
            Returns:
                bool: True if any value in the dictionary is a list containing dictionaries, False otherwise.
            """
            return any(isinstance(val, list) and contains_dict(val) for val in d.values())

        def flatten(data):
            """
            Flatten nested dictionaries within lists in a data structure.
            
            Args:
                data (dict): The dictionary to flatten.
            
            Returns:
                list: A list of flattened dictionaries.
            """
            flattened_data = []
            
            if not isinstance(data, dict):
                raise TypeError("Input data must be a dictionary.")
            
            if check_dict_values(data):
                for key, val in data.items():
                    if isinstance(val, list):
                        for i in range(len(val)):
                            item = val[i]
                            if isinstance(item, dict):
                                flattened_data += flatten(item)
                                val[i] = None  # Remove nested dictionary
                        # Set the list to None if all its elements are None
                        data[key] = None if all(item is None for item in val) else val
                # Append modified data once nested dicts have been removed
                flattened_data.append(data)
            else:
                flattened_data.append(data)
            
            return flattened_data

        flattened_data = []
        try:
            Extractor = self.get_extractor(element)
            extracted_info = Extractor.extract_info()
            if extracted_info:
                flattened_data = flatten(extracted_info)
            

            for data in flattened_data:
                entity_id = data.get('entityToken') or data.get('tempId')   
                if entity_id not in self.nodes:
                    self.nodes[entity_id] = data
                else:
                    self.add_or_update(self.nodes[entity_id],data)
                
        except Exception as e:
            self.logger.error(f"""
                              Error in extract_data: {str(e)}\n
                              Failed:\n{traceback.format_exc()}
                            """)
        flattened_data = {}
        
        def _extract_and_store(data):
            if not isinstance(data, dict):
                return None
            
            entity_id = data.get('entityToken') or data.get('tempId')
            if entity_id:
                flattened_data[entity_id] = data

            for key, value in list(data.items()):
                if isinstance(value, list):
                    nested_ids = []
                    for item in value:
                        if isinstance(item, dict):
                            nested_id = _extract_and_store(item, entity_id)
                            nested_ids.append(nested_id)
                        else:
                            nested_ids.append(item)
                    data[key] = nested_ids
                elif isinstance(value, dict):
                    nested_id = _extract_and_store(value, entity_id)
                    data[key] = nested_id
                    data.pop(key, None)
            
            return entity_id

    def update_nodes(self, flattened_data):
        """
        Updates the nodes with the flattened data.

        Args:
            flattened_data (dict): The flattened data to update the nodes with.

        Returns:
            None
        """
        for entity_id, data in flattened_data.items():
            if entity_id not in self.nodes:
                self.nodes[entity_id] = data
            else:
                self.add_or_update(self.nodes[entity_id], data)
            
    def add_or_update(self, stored_dict: Dict, other_dict: Dict):
        for key, value in other_dict.items():
            if key not in stored_dict:
                stored_dict[key] = value
            else:
                if stored_dict[key] != value:
                    # Combining the values into a List
                    if isinstance(stored_dict[key],list):
                        stored_dict[key] = stored_dict[key].append(value)
                    else:
                        stored_dict[key] = [stored_dict[key], value]

    def extract_sketch_entities(self, sketch: Sketch) -> None:
        """
        Helper function to extract entities from a sketch and link them.

        Args:
            sketch (Sketch): The sketch to extract entities from.
        """
        # TODO add try and catch
        for profile in sketch.profiles:
            self.extract_nested_data(profile)
            
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

    def _extract_feature(self, entity, comp: Component):
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
        self.logger.info(f'Extracting feature at timeline index {self.timelineIndex}: {entity.name}')
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
        self.logger.info(f'Extracting sketch at timeline index {self.timelineIndex}: {sketchEntity.name}')
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

            for face in body.faces:
                self.extract_data(face)

            for edge in body.edges:
                self.extract_data(edge)

            for vertex in body.vertices:
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

    def _extract_feature_face_relationship(self, comp: Component) -> None:
        """
        Extract data from a feature entity and process its BRep entities for startFaces, endFaces, and sideFaces.

        Args:
            comp (Component): The Fusion 360 component.
            
        This method iterates over all features in the given component, extracts the startFaces, endFaces,
        and sideFaces for each feature, and updates the `self.nodes` dictionary with the union of the new
        and existing faces for each feature.
        """
        for feature in comp.features:
            self._extract_faces(feature, 'faces', self.nodes)
            self._extract_faces(feature, 'startFaces', self.nodes)
            self._extract_faces(feature, 'endFaces', self.nodes)
            self._extract_faces(feature, 'sideFaces', self.nodes)

    def _extract_faces(self, feature, face_attr, nodes):
        """
        Extract and update the face entities for a given feature and face attribute.

        Args:
            feature (Feature): The Fusion 360 feature object from which to extract faces.
            face_attr (str): The attribute name of the faces to be extracted (e.g., 'startFaces', 'endFaces', 'sideFaces').
            nodes (dict): The dictionary to be updated with the face entities.

        This method retrieves the face entities associated with the given feature and face attribute,
        performs a union operation with any existing faces in the `nodes` dictionary, and updates the
        `nodes` dictionary with the result.
        """
        entityToken = getattr(feature, 'entityToken', None)
        if entityToken is not None:
            faces = [getattr(face, 'entityToken', None) for face in getattr(feature, face_attr, [])]
            if entityToken in nodes and face_attr in nodes[entityToken]:
                existing_faces = nodes[entityToken][face_attr]
                faces_union = list(set(existing_faces) | set(faces))
            else:
                faces_union = faces
            nodes[entityToken][face_attr] = faces_union

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
        self.current_faces: Set[str] = set()
        self.current_edges: Set[str] = set()
        self.current_vertices: Set[str] = set()

        self.extract_data(comp)
        self._extract_origin_construction_geometry(comp)

        for index in range(timeline.count):
            timelineObject = timeline.item(index)
            entity = timelineObject.entity
            self.timelineIndex = index

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

        self.extract_brep_entities(comp)
        self._extract_feature_face_relationship(comp)

        return list(self.nodes.values())
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
    timeline_nodes, timeline_relationships = orchestrator.extract_timeline_based_data()
"""
import logging
from typing import Optional, Tuple, Any, List, Dict, Set

import adsk.core
import adsk.fusion

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
        logger (logging.Logger, optional): The logger object for logging
            messages and errors.
    """
    # TODO Refactor methods
    def __init__(self,
                 design: adsk.fusion.Design,
                 logger: logging.Logger = None
                 ):
        self.design = design  # TODO  add type hinting
        self.logger = logger or logging.getLogger(__name__)
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.processed_relationships: set = set()
        self.timeline_index: str = 0

        self.new_faces: Set[str]
        self.new_edges: Set[str]
        self.new_vertices: Set[str]
        self.previous_faces: Set[str]
        self.previous_edges: Set[str]
        self.previous_vertices: Set[str]
        self.current_faces: Set[str]
        self.current_edges: Set[str]
        self.current_vertices: Set[str]

    def get_extractor(self, element: adsk.core.Base) -> BaseExtractor:
        """Get the appropriate extractor for the given CAD element.

        Args:
            element (adsk.core.Base): The CAD element.

        Returns:
            Extractor (BaseExtractor): The appropriate extractor for the
                element.
        """
        try:
            extractor_class: BaseExtractor = EXTRACTORS.get(
                element.objectType,
                BaseExtractor
                )
            return extractor_class(element)
        except Exception as e:  # TODO add specific exceptions
            exception_msg: str = (
                "Failed to get extractor for element "
                f"{element.objectType}: {str(e)}"
            )
            self.logger.error(exception_msg)
            raise

    def log_element_properties(self, element: adsk.core.Base):
        """
        Log the available methods and properties of the element for debugging

        Args:
            element (adsk.core.Base): Autodesk Fusion Element as interrogated
                by the API
        """
        available_methods = dir(element)
        element_properties_msg: str = (
            f"Available methods and properties for element "
            f"{element.objectType}: {available_methods}"
        )
        self.logger.debug(element_properties_msg)

    def extract_data(self,
                     element: adsk.core.Base
                     ) -> Optional[Dict[str, Any]]:
        """
        Extracts data from the given element using the appropriate extractor
        and stores it.

        Args:
            element (adsk.core.Base): The CAD element.

        Returns:
            Optional[Dict[str, Any]]: The extracted data.
        """
        try:
            if hasattr(element, 'isProxy') and element.isProxy:
                element = element.nativeObject

            # self.log_element_properties(element)

            extractor: BaseExtractor = self.get_extractor(element)
            extracted_info: Optional[Dict[str, Any]] = extractor.extract_info()
            if extracted_info:
                entity_id: str = extracted_info.get('entityToken', '')
                if entity_id and entity_id not in self.nodes:
                    self.nodes[entity_id] = extracted_info
                else:
                    self.add_or_update(
                        self.nodes.get(entity_id, {}),
                        extracted_info
                        )
            return extracted_info

        except Exception as e:  # TODO add specific exceptions
            general_exception_msg: str = f"""
                              Error in extract_data: {str(e)}\n
                              Failed:\n{traceback.format_exc()}
                            """
            self.logger.error(general_exception_msg)
            return None

    def add_or_update(self, stored_dict: Dict, other_dict: Dict):
        """Update the existing nodes with new information

        Args:
            stored_dict (Dict): Extracted dictionaries with node data
            other_dict (Dict): Dictionaries with new node data
        """
        for key, value in other_dict.items():
            if key not in stored_dict:
                stored_dict[key] = value
            else:
                if stored_dict[key] != value:
                    # Combining the values into a List
                    if isinstance(stored_dict[key], list):
                        stored_dict[key] = stored_dict[key].append(value)
                    else:
                        stored_dict[key] = [stored_dict[key], value]

    def extract_nested_data(self, element: adsk.core.Base):  # TODO add type hinting
        """
        Extracts nested data from the given element using the appropriate
        extractor and stores it.

        Args:
            element (adsk.core.Base): The CAD element.

        Returns:
            dict: The flattened data.
        """
        def contains_dict(lst):
            """
            Check if a list contains any dictionaries.

            Args:
                lst (list): The list to check.

            Returns:
                bool: True if any item in the list is a dictionary, False
                    otherwise.
            """
            return any(isinstance(item, dict) for item in lst)

        def check_dict_values(d):
            """
            Check if any values in a dictionary are lists that contain
            dictionaries.

            Args:
                d (dict): The dictionary to check.

            Returns:
                bool: True if any value in the dictionary is a list containing
                dictionaries, False otherwise.
            """
            return any(isinstance(val, list) and contains_dict(val)
                       for val in d.values())

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
                    self.add_or_update(self.nodes[entity_id], data)

        except Exception as e:  # TODO add specific exceptions
            self.logger.error(f"""
                              Error in extract_data: {str(e)}\n
                              Failed:\n{traceback.format_exc()}
                            """)
            flattened_data = {}

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

    def extract_sketch_entities(self, sketch: Sketch) -> None:
        """
        Helper function to extract entities from a sketch and link them.

        Args:
            sketch (Sketch): The sketch to extract entities from.
        """
        try:
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
        except Exception as e:  # TODO add specific exceptions
            general_exception_msg: str = f"""
                Error in extract_sketch_entities: {str(e)}\n
                {traceback.format_exc()}
                """
            self.logger.error(general_exception_msg)

    def _get_current_brep_entities(self, comp: adsk.fusion.Component) -> None:
        """
        Get the current BRep entities (faces, edges, vertices) of the
        component.

        Args:
            comp (adsk.fusion.Component): The Fusion 360 component.

        Returns:
            tuple: A tuple containing sets of current face, edge, and vertex
            tokens.
        """
        # TODO avoid repeating the body loop and share it across them
        try:
            self.current_faces = {face.entityToken
                                  for body in comp.bRepBodies
                                  for face in body.faces
                                  }
            self.current_edges = {edge.entityToken
                                  for body in comp.bRepBodies
                                  for edge in body.edges
                                  }
            self.current_vertices = {vertex.entityToken
                                     for body in comp.bRepBodies
                                     for vertex in body.vertices
                                     }
        except Exception as e:  # TODO add specific exceptions
            general_exception_msg: str = f"""
                Error in extract_sketch_entities: {str(e)}\n
                {traceback.format_exc()}
                """
            self.logger.error(general_exception_msg)

    def _process_new_entities(self,
                              new_entities: Set[str],
                              entity_type: str,
                              comp: adsk.fusion.Component) -> None:
        """
        Process new BRep entities (faces, edges, vertices) and add them to the extraction nodes and relationships.

        Args:
            new_entities (Set[str]): Set of new entity tokens.
            entity_type (str): Type of the BRep entity
                ('face', 'edge', 'vertex').
            comp (adsk.fusion.Component): The Fusion 360 component.
            feature_id (str): The ID of the feature.
            index (int): The timeline index.
        """
        if entity_type not in ENTITY_MAP:
            return None

        entity_attr, _ = ENTITY_MAP[entity_type]

        for token in new_entities:
            # TODO change new entities to dictionary and use entity type as key
            entity = next((e
                           for body in comp.bRepBodies
                           for e in getattr(body, entity_attr)
                           if e.entityToken == token), None)
            if entity:
                self.extract_data(entity)

    def _extract_feature(self, entity, comp: adsk.fusion.Component):
        """
        Extract data from a feature entity and process its BRep entities.

        Args:
            entity (Feature): The Fusion 360 feature entity.
            comp (adsk.fusion.Component): The Fusion 360 component.
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

    def _extract_sketch(self, sketch_entity: adsk.fusion.Sketch):
        """
        Extract data from a sketch entity and the contained entities.

        Args:
            sketchEntity (adsk.fusion.Sketch): The Fusion 360 sketch entity.
        """
        self.logger.info(f'Extracting sketch at timeline index {self.timeline_index}: {sketch_entity.name}')
        self.extract_data(sketch_entity)
        self.extract_sketch_entities(sketch_entity)

    def extract_brep_entities(self, comp: adsk.fusion.Component) -> None:
        """
        Extract final BRep entities and establish relationships.

        Args:
            comp (adsk.fusion.Component): The Fusion 360 component.
        """
        brep_extraction_msg: str = (
            'Extracting final BRep entities and establishing relationships'
        )
        self.logger.info(brep_extraction_msg)

        try:
            for body in comp.bRepBodies:
                self.extract_data(body)

                for face in body.faces:
                    self.extract_data(face)

                for edge in body.edges:
                    self.extract_data(edge)

                for vertex in body.vertices:
                    self.extract_data(vertex)
        except Exception as e:  # TODO add specific exceptions
            general_exception_msg: str = f"""
                Error in extract_brep_entities: {str(e)}\n
                {traceback.format_exc()}
                """
            self.logger.error(general_exception_msg)

    def _extract_other_entity(self, entity: adsk.core.Base) -> None:
        """Extract data for other entity types."""
        self.extract_data(entity)

    def _extract_origin_construction_geometry(
                                              self,
                                              comp: adsk.fusion.Component
                                              ) -> None:
        """
        Extracts construction planes and axes from the component.

        Args:
            comp (adsk.fusion.Component): The Fusion 360 component.
            component_id (str): The ID of the component node.
        """
        try:
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
        except Exception as e:  # TODO add specific exceptions
            general_exception_msg: str = f"""
                Error in _extract_origin_construction_geometry: {str(e)}\n
                {traceback.format_exc()}
                """
            self.logger.error(general_exception_msg)

    def _extract_feature_face_relationship(
                                           self,
                                           comp: adsk.fusion.Component
                                           ) -> None:
        """
        Extract data from a feature entity and process its BRep entities for
        startFaces, endFaces, and sideFaces.

        Args:
            comp (adsk.fusion.Component): The Fusion 360 component.

        This method iterates over all features in the given component, extracts
        the startFaces, endFaces, and sideFaces for each feature, and updates
        the `self.nodes` dictionary with the union of the new and existing
        faces for each feature.
        """
        for feature in comp.features:
            self._extract_faces(feature, 'faces', self.nodes)
            self._extract_faces(feature, 'startFaces', self.nodes)
            self._extract_faces(feature, 'endFaces', self.nodes)
            self._extract_faces(feature, 'sideFaces', self.nodes)

    def _extract_faces(self, feature, face_attr, nodes):
        """
        Extract and update the face entities for a given feature and face
        attribute.

        Args:
            feature (Feature): The Fusion 360 feature object from which to
            extract faces. face_attr (str): The attribute name of the faces to
            be extracted (e.g., 'startFaces', 'endFaces', 'sideFaces'). nodes
            (dict): The dictionary to be updated with the face entities.

        This method retrieves the face entities associated with the given
        feature and face attribute, performs a union operation with any
        existing faces in the `nodes` dictionary, and updates the `nodes`
        dictionary with the result.
        """
        entityToken: str = getattr(feature, 'entityToken', None)
        if entityToken is not None:
            faces: List[str] = [
                     getattr(face, 'entityToken', None)
                     for face in getattr(feature, face_attr, [])
                     ]
            if entityToken in nodes and face_attr in nodes[entityToken]:
                existing_faces = nodes[entityToken][face_attr]
                faces_union = list(set(existing_faces) | set(faces))
            else:
                faces_union = faces
            nodes[entityToken][face_attr] = faces_union

    def _extract_all_components(self) -> None:
        """
        Extracts all components from the given design.
        """
        try:
            all_components = self.design.allComponents
            for component in all_components:
                self.extract_data(component)
                self._extract_origin_construction_geometry(component)
        except Exception as e:  # TODO: Add specific exceptions if required
            general_exception_msg: str = f"""
                Error in _extract_all_components: {str(e)}\n
                {traceback.format_exc()}
            """
            self.logger.error(general_exception_msg)

    def _extract_all_parameters(self) -> None:
        """
        Extracts all parameters from the given design, including their parent component information.
        """
        try:
            all_parameters = self.design.allParameters
            for parameter in all_parameters:
                # Extract the data for each parameter
                self.extract_data(parameter)

                # Check if the parameter is a ModelParameter to extract parent component
                if isinstance(parameter, adsk.fusion.ModelParameter):
                    parent_component = parameter.component
                    if parent_component:
                        # Add the parent component data to the nodes
                        parameter_entity_token = parameter.entityToken
                        self.nodes[parameter_entity_token]['parentComponent'] = parent_component.entityToken

        except Exception as e:  # TODO: Add specific exceptions if required
            general_exception_msg: str = f"""
                Error in _extract_all_parameters: {str(e)}\n
                {traceback.format_exc()}
            """
            self.logger.error(general_exception_msg)

    def extract_timeline_based_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract data based on the timeline order.

        Returns:
            tuple: A tuple containing the list of nodes and relationships.
        """
        comp: adsk.fusion.Component = self.design.rootComponent
        timeline: adsk.fusion.Timeline = self.design.timeline

        # Reinitialise BREP sets
        self.previous_faces = set()
        self.previous_edges = set()
        self.previous_vertices = set()
        self.current_faces = set()
        self.current_edges = set()
        self.current_vertices = set()

        self._extract_all_components()
        self._extract_all_parameters()

        # Map to hold component ID -> { 'index': timeline_index, 'rootToken': root_component_token }
        timeline_to_component_map: Dict[str, Dict[str, Union[int, str]]] = {}


        for index in range(timeline.count):
            timelineObject = timeline.item(index)
            entity: adsk.core.Base = timelineObject.entity
            self.timeline_index = index

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
                elif isinstance(entity, adsk.fusion.Occurrence):
                    # Get the associated component ID and add it to the map
                    component_id = entity.nativeObject.component.id
                    root_component_token = comp.entityToken
                    # Map the component ID to its timeline index and root component token
                    timeline_to_component_map[component_id] = {
                        'index': index,
                        'rootToken': root_component_token
                    }
                    continue
                elif isinstance(entity, adsk.fusion.Component):
                    continue  # Components are already dealt with
                else:
                    self._extract_other_entity(entity)

                # Update previous sets
                self.previous_faces = self.current_faces.copy()
                self.previous_edges = self.current_edges.copy()
                self.previous_vertices = self.current_vertices.copy()

        self.process_components_with_timeline(timeline_to_component_map)

        all_components = self.design.allComponents
        for component in all_components:
            self.extract_brep_entities(component)
            self._extract_feature_face_relationship(component)

        return list(self.nodes.values())

    def process_components_with_timeline(self, timeline_to_component_map: Dict[str, int]) -> None:
        """
        Processes components to extract the entityToken and checks if the component's ID
        exists in the timeline_to_component_map. If the component's ID is found, it adds
        the timeline index to the component data, and entityToken of rootcomponent.

        Args:
            design (adsk.fusion.Design): The Fusion 360 design object.
            timeline_to_component_map (Dict[str, int]): A map of component IDs to their timeline indices.
        """
        all_components = self.design.allComponents
        for component in all_components:
            # Extract the entity token of the component
            entity_token = component.entityToken
            component_id = component.id

            # Log entityToken and component_id for debugging
            self.logger.info(f"Processing component with ID: {component_id}, EntityToken: {entity_token}")

            # Check if the component's ID exists in the timeline_to_component_map
            if component_id in timeline_to_component_map:
                # If found, get the timeline index from the map
                timeline_data = timeline_to_component_map[component_id]
                timeline_index = timeline_data['index']
                root_component_token = timeline_data['rootToken']

                # Add a new field 'timelineIndex' with the timeline index to the component's node data
                self.nodes[entity_token]['timelineIndex'] = timeline_index
                self.nodes[entity_token]['rootComponentToken'] = root_component_token

                # Log the association of the timelineIndex for debugging
                self.logger.info(f"Assigned timeline index {timeline_index} to component with ID: {component_id}")

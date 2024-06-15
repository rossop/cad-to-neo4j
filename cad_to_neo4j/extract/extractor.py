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
from .sketch import SketchExtractor, SketchPointExtractor, SketchCurveExtractor, SketchLineExtractor, ProfileExtractor
from .sketch.dimension import SketchDimensionExtractor
from .feature import ExtrudeFeatureExtractor, RevolveFeatureExtractor, FeatureExtractor
from .construction_plane_extractor import ConstructionPlaneExtractor
from .brep import BRepExtractor, BRepFaceExtractor, BRepEdgeExtractor

# adsk Debug
import adsk.core, traceback
app = adsk.core.Application.get()
ui = app.userInterface


__all__ = ['ExtractorOrchestrator']

EXTRACTORS = {
    'adsk::fusion::Sketch': SketchExtractor,
    'adsk::fusion::SketchPoint': SketchPointExtractor,
    'adsk::fusion::SketchCurve': SketchCurveExtractor,
    'adsk::fusion::SketchLine': SketchLineExtractor,
    'adsk::fusion::SketchDimension': SketchDimensionExtractor,
    'adsk::fusion::Profile': ProfileExtractor,
    'adsk::fusion::ExtrudeFeature': ExtrudeFeatureExtractor, 
    'adsk::fusion::RevolveFeature': RevolveFeatureExtractor, 
    'adsk::fusion::BRepBody': BRepExtractor, 
    'adsk::fusion::BRepFace': BRepFaceExtractor,
    'adsk::fusion::BRepEdge': BRepEdgeExtractor,
    'adsk::fusion::ConstructionPlane': ConstructionPlaneExtractor,
}

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
        self.nodes = []
        self.relationships = []
        self.processed_ids = set()
        self.processed_relationships = set()

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
        """Extracts data from the given element using the appropriate extractor.

        Args:
            element (Base): The CAD element.

        Returns:
            dict: The extracted data.
        """
        try:
            Extractor = self.get_extractor(element)
            extracted_info = Extractor.extract_info()
            if extracted_info:
                return extracted_info
            return None
        except Exception as e:
            self.logger.error(f"Error in extract_data: {str(e)}")
            self.logger.error(f"Failed:\n{traceback.format_exc()}")
            return None
        
    def add_relationship(self, from_id: str, to_id: str, rel_type: str) -> None:
        """
        Helper function to add a relationship and avoid duplication.

        Args:
            from_id (str): The ID of the originating node.
            to_id (str): The ID of the destination node.
            rel_type (str): The type of the relationship.
        """
        if (from_id, to_id, rel_type) not in self.processed_relationships:
            self.relationships.append({
                "from_id": from_id,
                "to_id": to_id,
                "rel_type": rel_type
            })
            self.processed_relationships.add((from_id, to_id, rel_type))

    def extract_and_append(self, entity: Base, parent_id: str, rel_type: str) -> Optional[str]:
        """
        Helper function to extract data and append nodes and relationships.

        Args:
            entity (Base): The CAD entity to extract data from.
            parent_id (str): The ID of the parent node.
            rel_type (str): The type of the relationship.

        Returns:
            str: The ID of the extracted entity, or None if extraction fails.
        """
        try:
            extracted_info = self.extract_data(entity)
            if extracted_info:
                entity_id = extracted_info['id_token']
                if entity_id not in self.processed_ids:
                    self.nodes.append(extracted_info)
                    self.processed_ids.add(entity_id)
                self.add_relationship(parent_id, entity_id, rel_type)
                return entity_id
        except Exception as e:
            self.logger.error(f"Error extracting and appending data for {entity}: {str(e)}")
            self.logger.error(f"Failed:\n{traceback.format_exc()}")
        return None
    
    def extract_brep_entity_data(self, brep_entity: Base, parent_id: str, timeline_index: Optional[int] = None) -> None:
        """
        Helper function to extract and append BRep entities.

        Args:
            brep_entity (Base): The BRep entity to extract data from.
            parent_id (str): The ID of the parent node.
            timeline_index (int, optional): The index of the timeline. Defaults to None.
        """
        entity_id = self.extract_and_append(brep_entity, parent_id, "CONTAINS")
        if not entity_id:
            return

        for face in brep_entity.faces:
            face_id = self.extract_and_append(face, entity_id, "CONTAINS")
            if face_id:
                self.add_timeline_tag(face_id, timeline_index)

            for edge in face.edges:
                edge_id = self.extract_and_append(edge, face_id, "CONTAINS")
                if edge_id:
                    self.add_timeline_tag(edge_id, timeline_index)

                for vertex in [edge.startVertex, edge.endVertex]:
                    vertex_id = self.extract_and_append(vertex, edge_id, "CONTAINS")
                    if vertex_id:
                        self.add_timeline_tag(vertex_id, timeline_index)

    def add_timeline_tag(self, entity_id: str, timeline_index: Optional[int]) -> None:
        """
        Adds a timeline tag to an entity if the timeline index is not None.

        Args:
            entity_id (str): The ID of the entity.
            timeline_index (Optional[int]): The index of the timeline. Defaults to None.
        """
        if timeline_index is not None:
            self.add_relationship(entity_id, f'timeline_index_{timeline_index}', 'HAS_TIMELINE_INDEX')

    def extract_sketch_profiles(self, sketch: Sketch, parent_id: str) -> Optional[str]:
        """
        Helper function to extract profiles from a sketch and link them.

        Args:
            sketch (Sketch): The sketch to extract profiles from.
            parent_id (str): The ID of the parent node.

        Returns:
            str: The ID of the extracted sketch, or None if extraction fails.
        """
        sketch_id = self.extract_and_append(sketch, parent_id, "CONTAINS")
        if not sketch_id:
            return None
        
        for profile in sketch.profiles:
            profile_id = self.extract_and_append(profile, sketch_id, "CONTAINS")
            if profile_id:
                self.add_relationship(sketch_id, profile_id, "CONTAINS")
        return sketch_id

    def extract_sketch(self, sketch: Sketch, sketch_id: str) -> None:
        """
        Helper function to extract entities from a sketch and link them.

        Args:
            sketch (Sketch): The sketch to extract entities from.
            sketch_id (str): The ID of the sketch node.
        """
        for point in sketch.sketchPoints:
            _ = self.extract_and_append(point, sketch_id, "CONTAINS")
        
        for curve in sketch.sketchCurves:
            _ = self.extract_and_append(curve, sketch_id, "CONTAINS")

        for dimension in sketch.sketchDimensions:
            _ = self.extract_and_append(dimension, sketch_id, "CONTAINS")

    def extract_component_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
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

            component_info = self.extract_data(comp)
            if component_info:
                self.nodes.append(component_info)
                component_id = component_info['id_token']

            for sketch in comp.sketches:
                sketch_id = self.extract_sketch_profiles(sketch, component_id)
                if sketch_id:
                    self.extract_sketch(sketch, sketch_id)

            for feat in comp.features:
                feature_id = self.extract_and_append(feat, component_id, "CONTAINS")
                if feature_id and hasattr(feat, 'bodies'):
                    for body in feat.bodies:
                        self.extract_brep_entity_data(body, feature_id)

            for body in comp.bRepBodies:
                _ = self.extract_and_append(body, component_id, "CONTAINS")

        return self.nodes, self.relationships

    def _get_current_brep_entities(self, comp: Component) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Get the current BRep entities (faces, edges, vertices) of the component.
        
        Args:
            comp (Component): The Fusion 360 component.

        Returns:
            tuple: A tuple containing sets of current face, edge, and vertex tokens.
        """
        current_faces = {face.entityToken for body in comp.bRepBodies for face in body.faces}
        current_edges = {edge.entityToken for body in comp.bRepBodies for edge in body.edges}
        current_vertices = {vertex.entityToken for body in comp.bRepBodies for vertex in body.vertices}

        return current_faces, current_edges, current_vertices

    def _process_new_entities(self, new_entities: Set[str], entity_type: str, comp: Component, feature_id: str, index: int):
        """
        Process new BRep entities (faces, edges, vertices) and add them to the extraction nodes and relationships.

        Args:
            new_entities (Set[str]): Set of new entity tokens.
            entity_type (str): Type of the BRep entity ('face', 'edge', 'vertex').
            comp (Component): The Fusion 360 component.
            feature_id (str): The ID of the feature.
            index (int): The timeline index.
        """
        entity_map = {
            'face': ('faces', BRepFaceExtractor),
            'edge': ('edges', BRepEdgeExtractor),
            'vertex': ('vertices', BaseExtractor)
        }
        if entity_type not in entity_map:
            return

        entity_attr, extractor_class = entity_map[entity_type]

        for token in new_entities:
            entity = next((e for body in comp.bRepBodies for e in getattr(body, entity_attr) if e.entityToken == token), None)
            if entity:
                extractor = extractor_class(entity)
                info = extractor.extract_info()
                if info:
                    self.nodes.append(info)
                    self.add_relationship(feature_id, info['id_token'], "CONTAINS")
                    self.add_timeline_tag(info['id_token'], index)

    def _extract_feature(self, entity: Feature, comp: Component, index: int, component_id: str, previous_faces: Set[str], previous_edges: Set[str], previous_vertices: Set[str]):
        """
        Extract data from a feature entity and process its BRep entities.

        Args:
            entity (Feature): The Fusion 360 feature entity.
            comp (Component): The Fusion 360 component.
            index (int): The timeline index.
            component_id (str): The ID of the component.
            previous_faces (Set[str]): Set of previous face tokens.
            previous_edges (Set[str]): Set of previous edge tokens.
            previous_vertices (Set[str]): Set of previous vertex tokens.
        """
        self.logger.info(f'Extracting feature at timeline index {index}: {entity.name}')
        feature_id = self.extract_and_append(entity, component_id, "CONTAINS")
        if feature_id:
            current_faces, current_edges, current_vertices = self._get_current_brep_entities(comp)

            new_faces = current_faces - previous_faces
            new_edges = current_edges - previous_edges
            new_vertices = current_vertices - previous_vertices

            self._process_new_entities(new_faces, 'face', comp, feature_id, index)
            self._process_new_entities(new_edges, 'edge', comp, feature_id, index)
            self._process_new_entities(new_vertices, 'vertex', comp, feature_id, index)

    def _extract_sketch(self, entity: Sketch, comp: Component, index: int, component_id: str):
        """
        Extract data from a sketch entity and its profiles.

        Args:
            entity (Sketch): The Fusion 360 sketch entity.
            comp (Component): The Fusion 360 component.
            index (int): The timeline index.
            component_id (str): The ID of the component.
        """
        self.logger.info(f'Extracting sketch at timeline index {index}: {entity.name}')
        sketch_id = self.extract_sketch_profiles(entity, component_id)
        if sketch_id:
            self.extract_sketch(entity, sketch_id)

    def extract_final_brep_entities(self, comp: Component, component_id: str) -> None:
        """
        Extract final BRep entities and establish relationships.

        Args:
            comp (Component): The Fusion 360 component.
            component_id (str): The ID of the component.
        """
        self.logger.info('Extracting final BRep entities and establishing relationships')

        for body in comp.bRepBodies:
            body_id = self.extract_and_append(body, component_id, "CONTAINS")
            if not body_id:
                continue

            for face in body.faces:
                face_id = self.extract_and_append(face, body_id, "CONTAINS")
                if not face_id:
                    continue

                for edge in face.edges:
                    edge_id = self.extract_and_append(edge, face_id, "CONTAINS")
                    if not edge_id:
                        continue

                    for vertex in [edge.startVertex, edge.endVertex]:
                        vertex_id = self.extract_and_append(vertex, edge_id, "CONTAINS")


    def extract_brep_relationships(self, comp: Component) -> None:
        """
        Extracts relationships among BRep entities (faces, edges, vertices).

        Args:
            comp (Component): The Fusion 360 component.
        """
        self.logger.info('Extracting BRep relationships')
        for body in comp.bRepBodies:
            for face in body.faces:
                face_id = face.entityToken

                for edge in face.edges:
                    edge_id = edge.entityToken
                    self.add_relationship(face_id, edge_id, "HAS_EDGE")

                    for vertex in [edge.startVertex, edge.endVertex]:
                        vertex_id = vertex.entityToken
                        self.add_relationship(edge_id, vertex_id, "HAS_VERTEX")
                        self.add_relationship(face_id, vertex_id, "HAS_VERTEX")

    def _extract_other_entity(self, entity: Base, component_id: Optional[str]) -> None:
        """Extract data for other entity types."""
        entity_info = self.extract_data(entity)
        if entity_info:
            self.nodes.append(entity_info)
            entity_id = entity_info['id_token']
            self.add_relationship(component_id, entity_id, "CONTAINS")

    def extract_timeline_based_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract data based on the timeline order.

        Returns:
            tuple: A tuple containing the list of nodes and relationships.
        """
        comp = self.design.rootComponent
        timeline = self.design.timeline

        previous_faces: Set[str] = set()
        previous_edges: Set[str] = set()
        previous_vertices: Set[str] = set()

        component_info = self.extract_data(comp)
        if component_info:
            self.nodes.append(component_info)
            component_id = component_info['id_token']
        else:
            component_id = None

        for index in range(timeline.count):
            timeline_object = timeline.item(index)
            entity = timeline_object.entity

            # Roll to current timeline
            self.logger.info(f'Rolling to timeline index {index}')
            timeline_object.rollTo(True)

            # Ensure the collections are updated after rolling the timeline
            current_faces, current_edges, current_vertices = self._get_current_brep_entities(comp)

            if entity:
                if isinstance(entity, Feature):
                    self._extract_feature(entity, comp, index, component_id, previous_faces, previous_edges, previous_vertices)
                elif isinstance(entity, Sketch):
                    self._extract_sketch(entity, comp, index, component_id)
                else:
                     self._extract_other_entity(entity, component_id)

                # Update previous sets
                previous_faces = current_faces.copy()
                previous_edges = current_edges.copy()
                previous_vertices = current_vertices.copy()
    
        # Extract final BRep entities and establish relationships
        self.extract_brep_relationships(comp)

        return self.nodes, self.relationships
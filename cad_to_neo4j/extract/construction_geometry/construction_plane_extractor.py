"""
Construction Plane Extractor Module

This module provides an extractor class for extracting information from ConstructionPlane objects.

Classes:
    - ConstructionPlaneExtractor: Extractor for ConstructionPlane objects.
"""
from typing import Optional, Dict, List, Any
import adsk.core
from adsk.fusion import (
    ConstructionPlane, 
    ConstructionPlaneDefinition, 
    ConstructionPlaneAtAngleDefinition, 
    ConstructionPlaneByPlaneDefinition, 
    ConstructionPlaneDistanceOnPathDefinition, 
    ConstructionPlaneMidplaneDefinition, 
    ConstructionPlaneOffsetDefinition, 
    ConstructionPlaneTangentAtPointDefinition, 
    ConstructionPlaneTangentDefinition, 
    ConstructionPlaneThreePointsDefinition, 
    ConstructionPlaneTwoEdgesDefinition,
    )
from ..base_extractor import BaseExtractor
import traceback
from ...utils.general_utils import nested_getattr

__all__ = ['ConstructionPlaneExtractor']

class ConstructionPlaneExtractor(BaseExtractor):
    """
    Extractor for ConstructionPlane objects.
    
    This class provides methods to extract various properties from a ConstructionPlane object.

    Attributes:
        plane (ConstructionPlane): The construction plane object to extract data from.
    """

    def __init__(self, obj: ConstructionPlane):
        """Initialises the ConstructionPlaneExtractor with a construction plane object.

        Args:
            obj: The construction plane object to extract information from.
        """
        super().__init__(obj)

    @property
    def geometry(self) -> Optional[Dict[str, List[float]]]:
        """Extracts the geometry of the construction plane.

        Returns:
            dict: A dictionary containing the origin and normal vector of the construction plane.
        """
        try:
            origin = nested_getattr(self._obj, 'geometry.origin', None)
            normal =  nested_getattr(self._obj, 'geometry.normal', None)
            if normal is not None and origin is not None:
                return {

                    'origin' : [
                        getattr(origin, 'x', None),
                        getattr(origin, 'y', None),
                        getattr(origin, 'z', None),
                    ],
                    'normal' : [
                        getattr(normal, 'x', None),
                        getattr(normal, 'y', None),
                        getattr(normal, 'z', None),
                    ],
                }
            else:
                return None
        except AttributeError as e:
            self.logger.error(f'Error extracting geometry: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def timelineObject(self) -> Optional[str]:
        """Extracts the timeline object associated with this construction plane.

        Returns:
            List[str]: The timeline object, or an empty list if not available.
        """
        try:
            return nested_getattr(self._obj, 'timelineObject.entity.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting timeline object: {e}\n{traceback.format_exc()}')
            return None

    @property
    def isParametric(self) -> Optional[bool]:
        """Extracts the parametric state of the construction plane.

        Returns:
            bool: True if the construction plane is parametric, False otherwise.
        """
        try:
            return getattr(self._obj, 'isParametric', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting parametric state: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def isVisible(self) -> Optional[bool]:
        """Indicates if the construction plane is visible.

        Returns:
            bool: True if the construction plane is visible, False otherwise.
        """
        try:
            return getattr(self._obj, 'isVisible', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting visibility: {e}\n{traceback.format_exc()}')
            return None
    
    @property
    def healthState(self) -> Optional[str]:
        """Extracts the current health state of this plane.

        Returns:
            str: The health state, or None if not available.
        """
        try:
            return getattr(self._obj, 'healthState', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting health state: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def errorOrWarningMessage(self) -> Optional[str]:
        """Extracts the error or warning message, if any, associated with the health state of this plane.

        Returns:
            str: The error or warning message, or None if not available.
        """
        try:
            return getattr(self._obj, 'errorOrWarningMessage', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting error or warning message: {e}\n{traceback.format_exc()}')
            return None

    @property
    def transform(self) -> Optional[List[float]]:
        """Extracts the transform of the Construction Plane object.

        Returns:
            List[float]: The transform of the Construction Plane object.
        """
        try:
            transform = nested_getattr(self._obj, 'transform', None)
            if transform:
                return [
                    transform.asArray()[0],  # 'm11'
                    transform.asArray()[1],  # 'm12'
                    transform.asArray()[2],  # 'm13'
                    transform.asArray()[3],  # 'm14'
                    transform.asArray()[4],  # 'm21'
                    transform.asArray()[5],  # 'm22'
                    transform.asArray()[6],  # 'm23'
                    transform.asArray()[7],  # 'm24'
                    transform.asArray()[8],  # 'm31'
                    transform.asArray()[9],  # 'm32'
                    transform.asArray()[10], # 'm33'
                    transform.asArray()[11], # 'm34'
                    transform.asArray()[12], # 'm41'
                    transform.asArray()[13], # 'm42'
                    transform.asArray()[14], # 'm43'
                    transform.asArray()[15], # 'm44'
                ]
            return None
        except AttributeError as e:
            self.logger.error(f'Error extracting transform matrix: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def base_feature(self) -> Optional[str]:
        """Extracts the base feature associated with this plane, if available.

        Returns:
            str: The base feature, or None if not available.
        """
        try:
            return getattr(self._obj, 'baseFeature', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting base feature: {e}\n{traceback.format_exc()}')
            return None

        
    def extract_definition_info(self, definition: ConstructionPlaneDefinition) -> Optional[Dict[str, Any]]:
        """Extracts the definition information for the construction plane.

        Args:
            definition (ConstructionPlaneDefinition): The construction plane definition object.

        Returns:
            dict: A dictionary containing the extracted definition information.
        """
        try:
            self.logger.info(f'Extracting definition info for type: {type(definition)}')
            if isinstance(definition, ConstructionPlaneAtAngleDefinition):
                try:
                    linear_entity = definition.linearEntity
                except RuntimeError:
                    linear_entity = None
                try:
                    # TODO fix issues with getting planar identity when plan at an angle has no plane
                    # This should be done without the need for try and except
                    planar_entity = definition.planarEntity
                except RuntimeError:
                    planar_entity = None
                
                
                return {
                    'definition_type': 'AtAngle',
                    'angle': definition.angle.value,
                    'linear_entity': linear_entity.entityToken if linear_entity is not None else None,
                    'planar_entity': planar_entity.entityToken if planar_entity is not None else None
                }
                
            elif isinstance(definition, ConstructionPlaneByPlaneDefinition):
                plane = getattr(definition, 'plane', None)
                if plane is not None:
                    return {
                        'definition_type': 'ByPlane',
                        'plane_normal': [
                                plane.normal.x,
                                plane.normal.y,
                                plane.normal.z,
                        ],
                        'plane_origin': [
                                plane.origin.x,
                                plane.origin.y,
                                plane.origin.z,
                        ],
                    }
                else:
                    self.logger.error(f'Missing plane in ConstructionPlaneByPlaneDefinition: plane={plane}')
                    return None
                
            elif isinstance(definition, ConstructionPlaneDistanceOnPathDefinition):
                path_entity = getattr(definition, 'pathEntity', None)
                if path_entity is not None:
                    return {
                        'definition_type': 'DistanceOnPath',
                        'path_entity': path_entity.entityToken,
                        'distance': definition.distance.value
                    }
                else:
                    self.logger.error(f'Missing pathEntity in ConstructionPlaneDistanceOnPathDefinition: path_entity={path_entity}')
                    return None
                
            elif isinstance(definition, ConstructionPlaneMidplaneDefinition):
                planar_entity_one = getattr(definition, 'planarEntityOne', None)
                planar_entity_two = getattr(definition, 'planarEntityTwo', None)
                if planar_entity_one is not None and planar_entity_two is not None:
                    return {
                        'definition_type': 'Midplane',
                        'planar_entity_one': planar_entity_one.entityToken,
                        'planar_entity_two': planar_entity_two.entityToken
                    }
                else:
                    self.logger.error(f'Missing entities in ConstructionPlaneMidplaneDefinition: '
                                    f'planar_entity_one={planar_entity_one}, planar_entity_two={planar_entity_two}')
                    return None
                
            elif isinstance(definition, ConstructionPlaneOffsetDefinition):
                planar_entity = getattr(definition, 'planarEntity', None)
                if planar_entity is not None:
                    return {
                        'definition_type': 'Offset',
                        'offset': definition.offset.value,
                        'planar_entity': planar_entity.entityToken
                    }
                else:
                    self.logger.error(f'Missing planarEntity in ConstructionPlaneOffsetDefinition: planar_entity={planar_entity}')
                    return None
                
            elif isinstance(definition, ConstructionPlaneTangentAtPointDefinition):
                tangent_face = getattr(definition, 'tangentFace', None)
                point_entity = getattr(definition, 'pointEntity', None)
                if tangent_face is not None and point_entity is not None:
                    return {
                        'definition_type': 'TangentAtPoint',
                        'tangent_face': tangent_face.entityToken,
                        'point_entity': point_entity.entityToken
                    }
                else:
                    self.logger.error(f'Missing entities in ConstructionPlaneTangentAtPointDefinition: '
                                    f'tangent_face={tangent_face}, point_entity={point_entity}')
                    return None
            elif isinstance(definition, ConstructionPlaneTangentDefinition):
                tangent_face = getattr(definition, 'tangentFace', None)
                planar_entity = getattr(definition, 'planarEntity', None)
                if tangent_face is not None and planar_entity is not None:
                    return {
                        'definition_type': 'Tangent',
                        'angle': definition.angle.value,
                        'tangent_face': tangent_face.entityToken,
                        'planar_entity': planar_entity.entityToken
                    }
                else:
                    self.logger.error(f'Missing entities in ConstructionPlaneTangentDefinition: '
                                    f'tangent_face={tangent_face}, planar_entity={planar_entity}')
                    return None
                
            elif isinstance(definition, ConstructionPlaneThreePointsDefinition):
                point_entity_one = getattr(definition, 'pointEntityOne', None)
                point_entity_two = getattr(definition, 'pointEntityTwo', None)
                point_entity_three = getattr(definition, 'pointEntityThree', None)
                if point_entity_one is not None and point_entity_two is not None and point_entity_three is not None:
                    return {
                        'definition_type': 'ThreePoints',
                        'point_entity_one': point_entity_one.entityToken,
                        'point_entity_two': point_entity_two.entityToken,
                        'point_entity_three': point_entity_three.entityToken
                    }
                else:
                    self.logger.error(f'Missing entities in ConstructionPlaneThreePointsDefinition: '
                                    f'point_entity_one={point_entity_one}, point_entity_two={point_entity_two}, point_entity_three={point_entity_three}')
                    return None
                
            elif isinstance(definition, ConstructionPlaneTwoEdgesDefinition):
                linear_entity_one = getattr(definition, 'linearEntityOne', None)
                linear_entity_two = getattr(definition, 'linearEntityTwo', None)
                if linear_entity_one is not None and linear_entity_two is not None:
                    return {
                        'definition_type': 'TwoEdges',
                        'linear_entity_one': linear_entity_one.entityToken,
                        'linear_entity_two': linear_entity_two.entityToken
                    }
                else:
                    self.logger.error(f'Missing entities in ConstructionPlaneTwoEdgesDefinition: '
                                    f'linear_entity_one={linear_entity_one}, linear_entity_two={linear_entity_two}')
                    return None
            else:
                self.logger.error(f'Unhandled definition type: {definition}')
                return None
        except AttributeError:
            self.logger.error(f'Failed to extract definition info:\n{traceback.format_exc()}')
            return None

    @property
    def definition(self) -> Optional[Dict[str, Any]]:
        """Extracts the definition information used by the construction plane."""
        definition_root = getattr(self._obj, 'definition', None)
        return self.extract_definition_info(definition_root)
    
    @property
    def parent(self) -> Optional[str]:
        """Extracts the parent of the ConstructionPoint object.

        Returns:
            str: The parent of the ConstructionPoint object.
        """
        return nested_getattr(self._obj, 'parent.entityToken', None)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the ConstructionPlane element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        construction_plane_info = {
            'parent': self.parent,
            'isParametric': self.isParametric,
            'isVisible': self.isVisible,
            'timelineObject': self.timelineObject,
            'base_feature': self.base_feature,
            'healthState': self.healthState,
            'errorOrWarningMessage': self.errorOrWarningMessage,
            'transform': self.transform,
        }
        
        # Add extent two information if available
        geometry_info = self.geometry
        if geometry_info is not None:
            construction_plane_info.update(geometry_info)
        
        # Add extent two information if available
        definition_info = self.definition
        if definition_info is not None:
            construction_plane_info.update(definition_info)

        return {**base_info, **construction_plane_info}

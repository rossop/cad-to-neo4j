"""
Construction Plane Extractor Module

This module provides an extractor class for extracting information from ConstructionPlane objects.

Classes:
    - ConstructionPlaneExtractor: Extractor for ConstructionPlane objects.
"""
from typing import Optional, Dict, List, Any
import adsk.core
from adsk.fusion import ConstructionPlane, ConstructionPlaneDefinition, ConstructionPlaneAtAngleDefinition, ConstructionPlaneByPlaneDefinition, ConstructionPlaneDistanceOnPathDefinition, ConstructionPlaneMidplaneDefinition, ConstructionPlaneOffsetDefinition, ConstructionPlaneTangentAtPointDefinition, ConstructionPlaneTangentDefinition, ConstructionPlaneThreePointsDefinition, ConstructionPlaneTwoEdgesDefinition
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
    def timeline_object(self) -> Optional[str]:
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
    def is_parametric(self) -> Optional[bool]:
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
    def is_visible(self) -> Optional[bool]:
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
    def health_state(self) -> Optional[str]:
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
    def error_or_warning_message(self) -> Optional[str]:
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
            if isinstance(definition, ConstructionPlaneAtAngleDefinition):
                return {
                    'definition_type': 'AtAngle',
                    'angle': definition.angle.value,
                    'linear_entity': definition.linearEntity.entityToken,
                    'planar_entity': definition.planarEntity.entityToken
                }
            elif isinstance(definition, ConstructionPlaneByPlaneDefinition):
                return {
                    'definition_type': 'ByPlane',
                    'plane': definition.plane.geometry
                }
            elif isinstance(definition, ConstructionPlaneDistanceOnPathDefinition):
                return {
                    'definition_type': 'DistanceOnPath',
                    'path_entity': definition.pathEntity.entityToken,
                    'distance': definition.distance.value
                }
            elif isinstance(definition, ConstructionPlaneMidplaneDefinition):
                return {
                    'definition_type': 'Midplane',
                    'planar_entity_one': definition.planarEntityOne.entityToken,
                    'planar_entity_two': definition.planarEntityTwo.entityToken
                }
            elif isinstance(definition, ConstructionPlaneOffsetDefinition):
                return {
                    'definition_type': 'Offset',
                    'offset': definition.offset.value,
                    'planar_entity': definition.planarEntity.entityToken
                }
            elif isinstance(definition, ConstructionPlaneTangentAtPointDefinition):
                return {
                    'definition_type': 'TangentAtPoint',
                    'tangent_face': definition.tangentFace.entityToken,
                    'point_entity': definition.pointEntity.entityToken
                }
            elif isinstance(definition, ConstructionPlaneTangentDefinition):
                return {
                    'definition_type': 'Tangent',
                    'angle': definition.angle.value,
                    'tangent_face': definition.tangentFace.entityToken,
                    'planar_entity': definition.planarEntity.entityToken
                }
            elif isinstance(definition, ConstructionPlaneThreePointsDefinition):
                return {
                    'definition_type': 'ThreePoints',
                    'point_entity_one': definition.pointEntityOne.entityToken,
                    'point_entity_two': definition.pointEntityTwo.entityToken,
                    'point_entity_three': definition.pointEntityThree.entityToken
                }
            elif isinstance(definition, ConstructionPlaneTwoEdgesDefinition):
                return {
                    'definition_type': 'TwoEdges',
                    'linear_entity_one': definition.linearEntityOne.entityToken,
                    'linear_entity_two': definition.linearEntityTwo.entityToken
                }
            return None
        except AttributeError:
            # TODO add logger
            # TODO understand which definition type the origin planes fit under
            return None

    @property
    def definition(self) -> Optional[Dict[str, Any]]:
        """Extracts the definition information used by the construction plane."""
        definition_root = getattr(self._obj, 'definition', None)
        return self.extract_definition_info(definition_root)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the ConstructionPlane element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        construction_plane_info = {
            'is_parametric': self.is_parametric,
            'is_visible': self.is_visible,
            'timeline_object': self.timeline_object,
            'base_feature': self.base_feature,
            'health_state': self.health_state,
            'error_or_warning_message': self.error_or_warning_message,
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

"""
Construction Plane Extractor Module

This module provides an extractor class for extracting information from ConstructionPlane objects.

Classes:
    - ConstructionPlaneExtractor: Extractor for ConstructionPlane objects.
"""
from typing import Optional, Dict, Any
import adsk.core
from adsk.fusion import ConstructionPlane, ConstructionPlaneDefinition, ConstructionPlaneAtAngleDefinition, ConstructionPlaneByPlaneDefinition, ConstructionPlaneDistanceOnPathDefinition, ConstructionPlaneMidplaneDefinition, ConstructionPlaneOffsetDefinition, ConstructionPlaneTangentAtPointDefinition, ConstructionPlaneTangentDefinition, ConstructionPlaneThreePointsDefinition, ConstructionPlaneTwoEdgesDefinition
from .base_extractor import BaseExtractor
import traceback
from ..utils.general_utils import nested_getattr

__all__ = ['ConstructionPlaneExtractor']

class ConstructionPlaneExtractor(BaseExtractor):
    """Extractor for extracting detailed information from ConstructionPlane objects."""

    def __init__(self, obj: ConstructionPlane):
        """Initialize the extractor with the ConstructionPlane element."""
        super().__init__(obj)

    @property
    def geometry(self) -> Optional[Dict[str, float]]:
        """Extracts the geometry of the construction plane.

        Returns:
            dict: A dictionary containing the origin and normal vector of the construction plane.
        """
        try:
            geometry = self._obj.geometry
            return {

                'origin' : [
                    nested_getattr(geometry, 'origin.x', None),
                    nested_getattr(geometry, 'origin.y', None),
                    nested_getattr(geometry, 'origin.z', None)
                ],
                'normal' : [
                    nested_getattr(geometry, 'normal.x', None),
                    nested_getattr(geometry, 'normal.y', None),
                    nested_getattr(geometry, 'normal.z', None)
                ],
            }
        except AttributeError as e:
            self.logger.error(f'Error extracting geometry: {e}\n{traceback.format_exc()}')
            return None

    @property
    def is_parametric(self) -> Optional[bool]:
        """Extracts the parametric state of the construction plane.

        Returns:
            bool: True if the construction plane is parametric, False otherwise.
        """
        try:
            return self._obj.isParametric
        except AttributeError as e:
            self.logger.error(f'Error extracting parametric state: {e}\n{traceback.format_exc()}')
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
        except AttributeError as e:
            self.logger.error(f'Error extracting definition info: {e}\n{traceback.format_exc()}')
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

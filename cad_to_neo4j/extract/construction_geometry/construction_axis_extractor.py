"""
Construction Axis Extractor Module

This module provides an extractor class for extracting information from ConstructionAxis objects.

Classes:
    - ConstructionAxisExtractor: Extractor for ConstructionAxis objects.
"""

from typing import Optional, Dict, Any
import adsk.core
from adsk.fusion import ConstructionAxis, ConstructionAxisDefinition, ConstructionAxisByLineDefinition, ConstructionAxisCircularFaceDefinition, ConstructionAxisEdgeDefinition, ConstructionAxisNormalToFaceAtPointDefinition, ConstructionAxisPerpendicularAtPointDefinition, ConstructionAxisTwoPlaneDefinition, ConstructionAxisTwoPointDefinition
from ..base_extractor import BaseExtractor
import traceback
from ...utils.extraction_utils import nested_getattr

__all__ = ['ConstructionAxisExtractor']


class ConstructionAxisExtractor(BaseExtractor):
    """
    Extractor for ConstructionAxis objects.
    
    This class provides methods to extract various properties from a ConstructionAxis object.

    Attributes:
        axis (ConstructionAxis): The construction axis object to extract data from.
    """

    def __init__(self, obj: ConstructionAxis):
        """Initialises the ConstructionAxisExtractor with a construction axis object.

        Args:
            obj: The construction axis object to extract information from.
        """
        super().__init__(obj)

    @property
    def geometry(self) -> Optional[Dict[str, Any]]:
        """Extracts the geometry of the construction axis.

        Returns:
            dict: A dictionary containing the origin and direction vector of the construction axis.
        """
        try:
            origin = nested_getattr(self._obj, 'geometry.origin', None)
            direction = nested_getattr(self._obj, 'geometry.direction', None)
            if origin is not None and direction is not None:
                return {
                    'origin': {
                        'x': getattr(origin, 'x', None),
                        'y': getattr(origin, 'y', None),
                        'z': getattr(origin, 'z', None),
                    },
                    'direction': {
                        'x': getattr(direction, 'x', None),
                        'y': getattr(direction, 'y', None),
                        'z': getattr(direction, 'z', None),
                    }
                }
            return None
        except AttributeError as e:
            self.logger.error(f'Error extracting geometry: {e}\n{traceback.format_exc()}')
            return None

    @property
    def timelineObject(self) -> Optional[str]:
        """Extracts the timeline object associated with this construction axis.

        Returns:
            str: The timeline object entity token, or None if not available.
        """
        try:
            return nested_getattr(self._obj, 'timelineObject.entity.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting timeline object: {e}\n{traceback.format_exc()}')
            return None

    @property
    def isParametric(self) -> Optional[bool]:
        """Extracts the parametric state of the construction axis.

        Returns:
            bool: True if the construction axis is parametric, False otherwise.
        """
        try:
            return getattr(self._obj, 'isParametric', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting parametric state: {e}\n{traceback.format_exc()}')
            return None

    @property
    def isVisible(self) -> Optional[bool]:
        """Indicates if the construction axis is visible.

        Returns:
            bool: True if the construction axis is visible, False otherwise.
        """
        try:
            return getattr(self._obj, 'isVisible', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting visibility: {e}\n{traceback.format_exc()}')
            return None

    @property
    def healthState(self) -> Optional[str]:
        """Extracts the current health state of the construction axis.

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
        """Extracts the error or warning message, if any, associated with the health state of the construction axis.

        Returns:
            str: The error or warning message, or None if not available.
        """
        try:
            return getattr(self._obj, 'errorOrWarningMessage', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting error or warning message: {e}\n{traceback.format_exc()}')
            return None

    def extract_definition_info(self, definition: ConstructionAxisDefinition) -> Optional[Dict[str, Any]]:
        """Extracts the definition information for the construction axis.

        Args:
            definition (ConstructionAxisDefinition): The construction axis definition object.

        Returns:
            dict: A dictionary containing the extracted definition information.
        """
        try:
            if isinstance(definition, ConstructionAxisByLineDefinition):
                origin = definition.axis.origin
                direction = definition.axis.direction
                return {
                    'definition_type': 'ByLine',
                    'origin': [
                            origin.x,
                            origin.y,
                            origin.z,
                        ] if origin is not None else None,
                    'direction': [
                            direction.x,
                            direction.y,
                            direction.z,
                        ] if direction is not None else None,
                }
            elif isinstance(definition, ConstructionAxisCircularFaceDefinition):
                return {
                    'definition_type': 'CircularFace',
                    'circular_face': definition.circularFace.entityToken
                }
            elif isinstance(definition, ConstructionAxisEdgeDefinition):
                return {
                    'definition_type': 'Edge',
                    'edge_entity': definition.edgeEntity.entityToken
                }
            elif isinstance(definition, ConstructionAxisNormalToFaceAtPointDefinition):
                return {
                    'definition_type': 'NormalToFaceAtPoint',
                    'face': definition.face.entityToken,
                    'point_entity': definition.pointEntity.entityToken
                }
            elif isinstance(definition, ConstructionAxisPerpendicularAtPointDefinition):
                return {
                    'definition_type': 'PerpendicularAtPoint',
                    'face': definition.face.entityToken,
                    'point': definition.point.entityToken
                }
            elif isinstance(definition, ConstructionAxisTwoPlaneDefinition):
                return {
                    'definition_type': 'TwoPlane',
                    'planar_entityOne': definition.planarEntityOne.entityToken,
                    'planar_entityTwo': definition.planarEntityTwo.entityToken
                }
            elif isinstance(definition, ConstructionAxisTwoPointDefinition):
                return {
                    'definition_type': 'TwoPoint',
                    'point_entityOne': definition.pointEntityOne.entityToken,
                    'point_entityTwo': definition.pointEntityTwo.entityToken
                }
            return None
        except AttributeError as e:
            self.logger.error(f'Error extracting definition info: {e}\n{traceback.format_exc()}')
            return None

    @property
    def definition(self) -> Optional[Dict[str, Any]]:
        """Extracts the definition information used by the construction axis."""
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
        """Extract all information from the ConstructionAxis element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        construction_axis_info = {
            'isParametric': self.isParametric,
            'isVisible': self.isVisible,
            'timelineObject': self.timelineObject,
            'healthState': self.healthState,
            'errorOrWarningMessage': self.errorOrWarningMessage,
            'parent': self.parent,

        }

        # Add geometry information if available
        geometry_info = self.geometry
        if geometry_info is not None:
            construction_axis_info.update(geometry_info)

        # Add definition information if available
        definition_info = self.definition
        if definition_info is not None:
            construction_axis_info.update(definition_info)

        return {**base_info, **construction_axis_info}

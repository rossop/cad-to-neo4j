"""
ConstructionPoint Extractor Module

This module provides an extractor class for extracting information from ConstructionPoint objects.

Classes:
    - ConstructionPointExtractor: Extractor for ConstructionPoint objects.
"""

from typing import Optional, Dict, List
from adsk.fusion import ConstructionPoint
from ..base_extractor import BaseExtractor
from ...utils.general_utils import nested_getattr
import adsk.core, traceback

__all__ = ['ConstructionPointExtractor']

class ConstructionPointExtractor(BaseExtractor):
    """Extractor for extracting detailed information from ConstructionPoint objects."""

    def __init__(self, element: ConstructionPoint):
        """Initialize the extractor with the ConstructionPoint element."""
        super().__init__(element)

    def extract_info(self) -> Dict[str, Optional[str]]:
        """Extract all information from the ConstructionPoint element.
        
        Returns:
            Dict[str, Optional[str]]: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        construction_point_info = {
            # 'geometry': self.geometry,
            'is_deletable': self.is_deletable,
            'is_light_bulb_on': self.is_light_bulb_on,
            'is_visible': self.is_visible,
            'parent': self.parent,
            'is_parametric': self.is_parametric,
            'timeline_object': self.timeline_object,
            'assembly_context': self.assembly_context,
            'native_object': self.native_object,
            'base_feature': self.base_feature,
            'health_state': self.health_state,
            'error_or_warning_message': self.error_or_warning_message
        }
        # # Add extent two information if available
        # definition_info = self.definition
        # if definition_info is not None:
        #     construction_point_info.update(definition_info)

        return {**basic_info, **construction_point_info}

    @property
    def geometry(self) -> Optional[List[float]]:
        """Extracts the geometry of the ConstructionPoint object.

        Returns:
            Dict[str, float]: The geometry of the ConstructionPoint object.
        """
        geometry = nested_getattr(self._obj, 'geometry', None)
        if geometry:
            return [
                geometry.x,
                geometry.y,
                geometry.z,
            ]
        return None

    @property
    def definition(self) -> Optional[Dict[str, Optional[str]]]:
        """Extracts the definition of the ConstructionPoint object.

        Returns:
            Dict[str, Optional[str]]: The definition of the ConstructionPoint object.
        """
        definition = nested_getattr(self._obj, 'definition', None)
        if definition:
            return self.extract_definition_info(definition)
        return None

    def extract_definition_info(self, definition) -> Dict[str, Optional[str]]:
        """Extracts detailed information about the construction point definition.

        Args:
            definition: The definition object of the ConstructionPoint.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing the definition information.
        """
        try:
            if isinstance(definition, adsk.fusion.ConstructionPointCenterDefinition):
                circular_entity = nested_getattr(definition, 'circularEntity.entityToken', None)
                return {'type': 'Center', 'circular_entity': circular_entity}
            elif isinstance(definition, adsk.fusion.ConstructionPointEdgePlaneDefinition):
                edge = nested_getattr(definition, 'edge.entityToken', None)
                plane = nested_getattr(definition, 'plane.entityToken', None)
                return {'type': 'EdgePlane', 'edge': edge, 'plane': plane}
            elif isinstance(definition, adsk.fusion.ConstructionPointPointDefinition):
                point_entity = nested_getattr(definition, 'pointEntity.entityToken', None)
                return {'type': 'Point', 'point_entity': point_entity}
            elif isinstance(definition, adsk.fusion.ConstructionPointThreePlanesDefinition):
                plane_one = nested_getattr(definition, 'planeOne.entityToken', None)
                plane_two = nested_getattr(definition, 'planeTwo.entityToken', None)
                plane_three = nested_getattr(definition, 'planeThree.entityToken', None)
                return {'type': 'ThreePlanes', 'plane_one': plane_one, 'plane_two': plane_two, 'plane_three': plane_three}
            elif isinstance(definition, adsk.fusion.ConstructionPointTwoEdgesDefinition):
                edge_one = nested_getattr(definition, 'edgeOne.entityToken', None)
                edge_two = nested_getattr(definition, 'edgeTwo.entityToken', None)
                return {'type': 'TwoEdges', 'edge_one': edge_one, 'edge_two': edge_two}
            else:
                return {'type': 'Unknown'}
        except AttributeError as e:
            return None
    @property
    def is_deletable(self) -> Optional[bool]:
        """Extracts the deletable status of the ConstructionPoint object.

        Returns:
            bool: The deletable status of the ConstructionPoint object.
        """
        return getattr(self._obj, 'isDeletable', None)

    @property
    def is_light_bulb_on(self) -> Optional[bool]:
        """Extracts the light bulb status of the ConstructionPoint object.

        Returns:
            bool: The light bulb status of the ConstructionPoint object.
        """
        return getattr(self._obj, 'isLightBulbOn', None)

    @property
    def is_visible(self) -> Optional[bool]:
        """Extracts the visibility status of the ConstructionPoint object.

        Returns:
            bool: The visibility status of the ConstructionPoint object.
        """
        return getattr(self._obj, 'isVisible', None)

    @property
    def parent(self) -> Optional[str]:
        """Extracts the parent of the ConstructionPoint object.

        Returns:
            str: The parent of the ConstructionPoint object.
        """
        return nested_getattr(self._obj, 'parent.entityToken', None)

    @property
    def is_parametric(self) -> Optional[bool]:
        """Extracts the parametric status of the ConstructionPoint object.

        Returns:
            bool: The parametric status of the ConstructionPoint object.
        """
        return getattr(self._obj, 'isParametric', None)

    @property
    def timeline_object(self) -> Optional[str]:
        """Extracts the timeline object of the ConstructionPoint object.

        Returns:
            str: The timeline object of the ConstructionPoint object.
        """
        return nested_getattr(self._obj, 'timelineObject.entityToken', None)

    @property
    def assembly_context(self) -> Optional[str]:
        """Extracts the assembly context of the ConstructionPoint object.

        Returns:
            str: The assembly context of the ConstructionPoint object.
        """
        return nested_getattr(self._obj, 'assemblyContext.entityToken', None)

    @property
    def native_object(self) -> Optional[str]:
        """Extracts the native object of the ConstructionPoint object.

        Returns:
            str: The native object of the ConstructionPoint object.
        """
        return nested_getattr(self._obj, 'nativeObject.entityToken', None)

    @property
    def base_feature(self) -> Optional[str]:
        """Extracts the base feature of the ConstructionPoint object.

        Returns:
            str: The base feature of the ConstructionPoint object.
        """
        return nested_getattr(self._obj, 'baseFeature.entityToken', None)

    @property
    def health_state(self) -> Optional[str]:
        """Extracts the health state of the ConstructionPoint object.

        Returns:
            str: The health state of the ConstructionPoint object.
        """
        return nested_getattr(self._obj, 'healthState', None)

    @property
    def error_or_warning_message(self) -> Optional[str]:
        """Extracts the error or warning message of the ConstructionPoint object.

        Returns:
            str: The error or warning message of the ConstructionPoint object.
        """
        return getattr(self._obj, 'errorOrWarningMessage', None)

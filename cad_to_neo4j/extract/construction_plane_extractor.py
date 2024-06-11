"""
Construction Plane Extractor Module

This module provides an extractor class for extracting information from ConstructionPlane objects.

Classes:
    - ConstructionPlaneExtractor: Extractor for ConstructionPlane objects.
"""
from typing import Optional, Dict, Any
import adsk.core
from adsk.fusion import ConstructionPlane
from .base_extractor import BaseExtractor
import traceback
from ..utils.general_utils import nested_getattr

__all__ = ['ConstructionPlaneExtractor']

class ConstructionPlaneExtractor(BaseExtractor):
    """Extractor for extracting detailed information from ConstructionPlane objects."""

    def __init__(self, element: ConstructionPlane):
        """Initialize the extractor with the ConstructionPlane element."""
        super().__init__(element)

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

    @property
    def is_visible(self) -> Optional[bool]:
        """Extracts the visibility state of the construction plane.

        Returns:
            bool: True if the construction plane is visible, False otherwise.
        """
        try:
            return self._obj.isVisible
        except AttributeError as e:
            self.logger.error(f'Error extracting visibility state: {e}\n{traceback.format_exc()}')
            return None

    @property
    def health_state(self) -> Optional[str]:
        """Extracts the health state of the construction plane.

        Returns:
            str: The health state of the construction plane.
        """
        try:
            return self._obj.healthState.name
        except AttributeError as e:
            self.logger.error(f'Error extracting health state: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the ConstructionPlane element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        construction_plane_info = {
            'is_parametric': self.is_parametric,
            'is_visible': self.is_visible,
            'health_state': self.health_state,
        }
                # Add extent two information if available
        geometry_info = self.geometry
        if geometry_info is not None:
            construction_plane_info.update(geometry_info)

        return {**base_info, **construction_plane_info}

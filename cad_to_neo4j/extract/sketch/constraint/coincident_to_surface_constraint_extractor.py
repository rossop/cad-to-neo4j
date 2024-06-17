"""
Coincident to Surface Constraint Extractor Module

This module provides an extractor class for extracting information from CoincidentToSurfaceConstraint objects.

Classes:
    - CoincidentToSurfaceConstraintExtractor: Extractor for CoincidentToSurfaceConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class CoincidentToSurfaceConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for CoincidentToSurfaceConstraint objects."""

    @property
    def point(self) -> Optional[str]:
        """Extracts the point of the constraint.

        Returns:
            str: The entity token of the point.
        """
        try:
            return nested_getattr(self._obj, 'point.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting point: {e}\n{traceback.format_exc()}')
            return None

    @property
    def surface(self) -> Optional[str]:
        """Extracts the surface of the constraint.

        Returns:
            str: The entity token of the surface.
        """
        try:
            return nested_getattr(self._obj, 'surface.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting surface: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the CoincidentToSurfaceConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'point': self.point,
            'surface': self.surface,
        }
        return {**base_info, **constraint_info}

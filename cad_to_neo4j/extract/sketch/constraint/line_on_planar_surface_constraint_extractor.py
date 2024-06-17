"""
Line On Planar Surface Constraint Extractor Module

This module provides an extractor class for extracting information from LineOnPlanarSurfaceConstraint objects.

Classes:
    - LineOnPlanarSurfaceConstraintExtractor: Extractor for LineOnPlanarSurfaceConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class LineOnPlanarSurfaceConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for LineOnPlanarSurfaceConstraint objects."""

    @property
    def line(self) -> Optional[str]:
        """Extracts the line of the constraint.

        Returns:
            str: The entity token of the line.
        """
        try:
            return nested_getattr(self._obj, 'line.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting line: {e}\n{traceback.format_exc()}')
            return None

    @property
    def planar_surface(self) -> Optional[str]:
        """Extracts the planar surface of the constraint.

        Returns:
            str: The entity token of the planar surface.
        """
        try:
            return nested_getattr(self._obj, 'planarSurface.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting planarSurface: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the LineOnPlanarSurfaceConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'line': self.line,
            'planar_surface': self.planar_surface,
        }
        return {**base_info, **constraint_info}

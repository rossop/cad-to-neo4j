"""
Line On Planar Surface Constraint Extractor Module

This module provides an extractor class for extracting information from LineOnPlanarSurfaceConstraint objects.

Classes:
    - LineOnPlanarSurfaceConstraintExtractor: Extractor for LineOnPlanarSurfaceConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from adsk.fusion import LineOnPlanarSurfaceConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class LineOnPlanarSurfaceConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for LineOnPlanarSurfaceConstraint objects."""

    def __init__(self, obj: LineOnPlanarSurfaceConstraint):
        """
        Initialise the extractor with the LineOnPlanarSurfaceConstraint element.

        Args:
            obj (LineOnPlanarSurfaceConstraint): The LineOnPlanarSurfaceConstraint object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the LineOnPlanarSurfaceConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'line': self.line,
            'planarSurface': self.planarSurface,
        }
        return {**base_info, **constraint_info}

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
    def planarSurface(self) -> Optional[str]:
        """Extracts the planar surface of the constraint.

        Returns:
            str: The entity token of the planar surface.
        """
        try:
            return nested_getattr(self._obj, 'planarSurface.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting planarSurface: {e}\n{traceback.format_exc()}')
            return None

"""
Coincident to Surface Constraint Extractor Module

This module provides an extractor class for extracting information from CoincidentToSurfaceConstraint objects.

Classes:
    - CoincidentToSurfaceConstraintExtractor: Extractor for CoincidentToSurfaceConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from adsk.fusion import CoincidentToSurfaceConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class CoincidentToSurfaceConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for CoincidentToSurfaceConstraint objects."""

    def __init__(self, obj: CoincidentToSurfaceConstraint):
        """
        Initialise the extractor with the CoincidentToSurfaceConstraint element.

        Args:
            obj (CoincidentToSurfaceConstraint): The CoincidentToSurfaceConstraint object to extract information from.
        """
        super().__init__(obj)

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

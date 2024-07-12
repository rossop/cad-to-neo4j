"""
Mid Point Constraint Extractor Module

This module provides an extractor class for extracting information from MidPointConstraint objects.

Classes:
    - MidPointConstraintExtractor: Extractor for MidPointConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr
class MidPointConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for MidPointConstraint objects."""

    @property
    def point(self) -> Optional[str]:
        """Extracts the point of the mid point constraint.

        Returns:
            str: The entity token of the point.
        """
        try:
            return nested_getattr(self._obj,'point.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting point: {e}\n{traceback.format_exc()}')
            return None

    @property
    def midPointCurve(self) -> Optional[str]:
        """Extracts the mid point curve of the mid point constraint.

        Returns:
            str: The entity token of the mid point curve.
        """
        try:
            return nested_getattr(self._obj,'midPointCurve.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting midPointCurve: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the MidPointConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'point': self.point,
            'midPointCurve': self.midPointCurve,
        }
        return {**base_info, **constraint_info}
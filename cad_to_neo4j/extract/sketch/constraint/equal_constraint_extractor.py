"""
Equal Constraint Extractor Module

This module provides an extractor class for extracting information from EqualConstraint objects.

Classes:
    - EqualConstraintExtractor: Extractor for EqualConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class EqualConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for EqualConstraint objects."""

    @property
    def curve_one(self) -> Optional[str]:
        """Extracts the first curve of the constraint.

        Returns:
            str: The entity token of the first curve.
        """
        try:
            return nested_getattr(self._obj, 'curveOne.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting curveOne: {e}\n{traceback.format_exc()}')
            return None

    @property
    def curve_two(self) -> Optional[str]:
        """Extracts the second curve of the constraint.

        Returns:
            str: The entity token of the second curve.
        """
        try:
            return nested_getattr(self._obj, 'curveTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting curveTwo: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the EqualConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'curve_one': self.curve_one,
            'curve_two': self.curve_two,
        }
        return {**base_info, **constraint_info}

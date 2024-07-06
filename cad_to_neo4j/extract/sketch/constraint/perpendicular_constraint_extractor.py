### `extract/sketch/constraint/perpendicular_constraint_extractor.py`
"""
Perpendicular Constraint Extractor Module

This module provides an extractor class for extracting information from PerpendicularConstraint objects.

Classes:
    - PerpendicularConstraintExtractor: Extractor for PerpendicularConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class PerpendicularConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for PerpendicularConstraint objects."""

    @property
    def line_one(self) -> Optional[str]:
        """Extracts the first line of the perpendicular constraint.

        Returns:
            str: The entity token of the first line.
        """
        try:
            return nested_getattr(self._obj, 'lineOne.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting lineOne: {e}\n{traceback.format_exc()}')
            return None

    @property
    def line_two(self) -> Optional[str]:
        """Extracts the second line of the perpendicular constraint.

        Returns:
            str: The entity token of the second line.
        """
        try:
            return nested_getattr(self._obj, 'lineTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting lineTwo: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the PerpendicularConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'line_one': self.line_one,
            'line_two': self.line_two,
        }
        return {**base_info, **constraint_info}
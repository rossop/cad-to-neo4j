"""
Parallel Constraint Extractor Module

This module provides an extractor class for extracting information from ParallelConstraint objects.

Classes:
    - ParallelConstraintExtractor: Extractor for ParallelConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class ParallelConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for ParallelConstraint objects."""

    @property
    def line_one(self) -> Optional[str]:
        """Extracts the first line of the parallel constraint.

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
        """Extracts the second line of the parallel constraint.

        Returns:
            str: The entity token of the second line.
        """
        try:
            return nested_getattr(self._obj, 'lineTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting lineTwo: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the ParallelConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'line_one': self.line_one,
            'line_two': self.line_two,
        }
        return {**base_info, **constraint_info}

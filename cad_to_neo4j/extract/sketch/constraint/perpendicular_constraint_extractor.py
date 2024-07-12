### `extract/sketch/constraint/perpendicular_constraint_extractor.py`
"""
Perpendicular Constraint Extractor Module

This module provides an extractor class for extracting information from PerpendicularConstraint objects.

Classes:
    - PerpendicularConstraintExtractor: Extractor for PerpendicularConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from adsk.fusion import PerpendicularConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class PerpendicularConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for PerpendicularConstraint objects."""

    def __init__(self, obj: PerpendicularConstraint):
        """
        Initialise the extractor with the PerpendicularConstraint element.

        Args:
            obj (PerpendicularConstraint): The PerpendicularConstraint object to extract information from.
        """
        super().__init__(obj)

    @property
    def lineOne(self) -> Optional[str]:
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
    def lineTwo(self) -> Optional[str]:
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
            'lineOne': self.lineOne,
            'lineTwo': self.lineTwo,
        }
        return {**base_info, **constraint_info}
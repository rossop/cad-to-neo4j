"""
Collinear Constraint Extractor Module

This module provides an extractor class for extracting information from CollinearConstraint objects.

Classes:
    - CollinearConstraintExtractor: Extractor for CollinearConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from adsk.fusion import CollinearConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class CollinearConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for CollinearConstraint objects."""

    def __init__(self, obj: CollinearConstraint):
        """
        Initialise the extractor with the CollinearConstraint element.

        Args:
            obj (CollinearConstraint): The CollinearConstraint object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the CollinearConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'lineOne': self.lineOne,
            'lineTwo': self.lineTwo,
        }
        return {**base_info, **constraint_info}

    @property
    def lineOne(self) -> Optional[str]:
        """Extracts the first line of the constraint.

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
        """Extracts the second line of the constraint.

        Returns:
            str: The entity token of the second line.
        """
        try:
            return nested_getattr(self._obj, 'lineTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting lineTwo: {e}\n{traceback.format_exc()}')
            return None

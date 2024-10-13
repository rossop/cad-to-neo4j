"""
Horizontal Points Constraint Extractor Module

This module provides an extractor class for extracting information from HorizontalPointsConstraint objects.

Classes:
    - HorizontalPointsConstraintExtractor: Extractor for HorizontalPointsConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from adsk.fusion import HorizontalPointsConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class HorizontalPointsConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for HorizontalPointsConstraint objects."""
    
    def __init__(self, obj: HorizontalPointsConstraint):
        """
        Initialise the extractor with the HorizontalPointsConstraint element.

        Args:
            obj (HorizontalPointsConstraint): The HorizontalPointsConstraint object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the HorizontalPointsConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'point_one': self.point_one,
            'point_two': self.point_two,
        }
        return {**base_info, **constraint_info}

    @property
    def point_one(self) -> Optional[str]:
        """Extracts the first point of the constraint.

        Returns:
            str: The entity token of the first point.
        """
        try:
            return nested_getattr(self._obj, 'pointOne.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting pointOne: {e}\n{traceback.format_exc()}')
            return None

    @property
    def point_two(self) -> Optional[str]:
        """Extracts the second point of the constraint.

        Returns:
            str: The entity token of the second point.
        """
        try:
            return nested_getattr(self._obj, 'pointTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting pointTwo: {e}\n{traceback.format_exc()}')
            return None

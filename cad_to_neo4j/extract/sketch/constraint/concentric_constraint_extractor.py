"""
Concentric Constraint Extractor Module

This module provides an extractor class for extracting information from ConcentricConstraint objects.

Classes:
    - ConcentricConstraintExtractor: Extractor for ConcentricConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class ConcentricConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for ConcentricConstraint objects."""

    @property
    def entity_one(self) -> Optional[str]:
        """Extracts the first entity of the constraint.

        Returns:
            str: The entity token of the first entity.
        """
        try:
            return nested_getattr(self._obj, 'entityOne.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting entityOne: {e}\n{traceback.format_exc()}')
            return None

    @property
    def entity_two(self) -> Optional[str]:
        """Extracts the second entity of the constraint.

        Returns:
            str: The entity token of the second entity.
        """
        try:
            return nested_getattr(self._obj, 'entityTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting entityTwo: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the ConcentricConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'entity_one': self.entity_one,
            'entity_two': self.entity_two,
        }
        return {**base_info, **constraint_info}

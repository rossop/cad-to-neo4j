"""
Concentric Constraint Extractor Module

This module provides an extractor class for extracting information from ConcentricConstraint objects.

Classes:
    - ConcentricConstraintExtractor: Extractor for ConcentricConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from adsk.fusion import ConcentricConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class ConcentricConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for ConcentricConstraint objects."""

    def __init__(self, obj: ConcentricConstraint):
        """
        Initialise the extractor with the ConcentricConstraint element.

        Args:
            obj (ConcentricConstraint): The ConcentricConstraint object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the ConcentricConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'entityOne': self.entityOne,
            'entityTwo': self.entityTwo,
        }
        return {**base_info, **constraint_info}

    @property
    def entityOne(self) -> Optional[str]:
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
    def entityTwo(self) -> Optional[str]:
        """Extracts the second entity of the constraint.

        Returns:
            str: The entity token of the second entity.
        """
        try:
            return nested_getattr(self._obj, 'entityTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting entityTwo: {e}\n{traceback.format_exc()}')
            return None

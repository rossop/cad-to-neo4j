"""
Parallel Constraint Extractor Module

This module provides an extractor class for extracting information from ParallelConstraint objects.

Classes:
    - ParallelConstraintExtractor: Extractor for ParallelConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from adsk.fusion import ParallelConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class ParallelConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for ParallelConstraint objects."""

    def __init__(self, obj: ParallelConstraint):
        """
        Initialise the extractor with the ParallelConstraint element.

        Args:
            obj (ParallelConstraint): The ParallelConstraint object to extract information from.
        """
        super().__init__(obj)

    @property
    def lineOne(self) -> Optional[str]:
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
    def lineTwo(self) -> Optional[str]:
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
            'lineOne': self.lineOne,
            'lineTwo': self.lineTwo,
        }
        return {**base_info, **constraint_info}

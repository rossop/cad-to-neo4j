"""
Symmetry Constraint Extractor Module

This module provides an extractor class for extracting information from SymmetryConstraint objects.

Classes:
    - SymmetryConstraintExtractor: Extractor for SymmetryConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from adsk.fusion import SymmetryConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class SymmetryConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for SymmetryConstraint objects."""

    def __init__(self, obj: SymmetryConstraint):
        """
        Initialise the extractor with the SymmetryConstraint element.

        Args:
            obj (SymmetryConstraint): The SymmetryConstraint object to extract information from.
        """
        super().__init__(obj)   

    @property
    def entityOne(self) -> Optional[str]:
        """Extracts the first entity of the symmetry constraint.

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
        """Extracts the second entity of the symmetry constraint.

        Returns:
            str: The entity token of the second entity.
        """
        try:
            return nested_getattr(self._obj, 'entityTwo.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting entityTwo: {e}\n{traceback.format_exc()}')
            return None

    @property
    def symmetry_line(self) -> Optional[str]:
        """Extracts the symmetry line of the symmetry constraint.

        Returns:
            str: The entity token of the symmetry line.
        """
        try:
            return nested_getattr(self._obj, 'symmetryLine.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting symmetryLine: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the SymmetryConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'entityOne': self.entityOne,
            'entityTwo': self.entityTwo,
            'symmetry_line': self.symmetry_line,
        }
        return {**base_info, **constraint_info}

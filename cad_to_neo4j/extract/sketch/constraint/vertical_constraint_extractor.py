"""
Vertical Constraint Extractor Module

This module provides an extractor class for extracting information from Vertical
Classes:
- VerticalConstraintExtractor: Extractor for VerticalConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from adsk.fusion import VerticalConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class VerticalConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for VerticalConstraint objects."""

    def __init__(self, obj: VerticalConstraint):
        """
        Initialise the extractor with the VerticalConstraint element.

        Args:
            obj (VerticalConstraint): The VerticalConstraint object to extract information from.
        """
        super().__init__(obj)

    @property
    def line(self) -> Optional[str]:
        """Extracts the line of the vertical constraint.

        Returns:
            str: The entity token of the line.
        """
        try:
            return nested_getattr(self._obj, 'line.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting line: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the VerticalConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'line': self.line,
        }
        return {**base_info, **constraint_info}
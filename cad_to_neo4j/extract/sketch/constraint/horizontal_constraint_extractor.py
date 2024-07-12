"""
Horizontal Constraint Extractor Module

This module provides an extractor class for extracting information from HorizontalConstraint objects.

Classes:
    - HorizontalConstraintExtractor: Extractor for HorizontalConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from adsk.fusion import HorizontalConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class HorizontalConstraintExtractor(GeometricConstraintExtractor):
    
    """Extractor for HorizontalConstraint objects."""
    def __init__(self, obj: HorizontalConstraint):
        """
        Initialise the extractor with the HorizontalConstraint element.

        Args:
            obj (HorizontalConstraint): The HorizontalConstraint object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the HorizontalConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'line': self.line,
        }
        return {**base_info, **constraint_info}

    @property
    def line(self) -> Optional[str]:
        """Extracts the line of the horizontal constraint.

        Returns:
            str: The entity token of the line.
        """
        try:
            return nested_getattr(self._obj, 'line.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting line: {e}\n{traceback.format_exc()}')
            return None
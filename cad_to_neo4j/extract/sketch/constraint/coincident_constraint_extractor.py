"""
Coincident Constraint Extractor Module

This module provides an extractor class for extracting information from CoincidentConstraint objects.

Classes:
    - CoincidentConstraintExtractor: Extractor for CoincidentConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class CoincidentConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for CoincidentConstraint objects."""

    @property
    def point(self) -> Optional[str]:
        """Extracts the point of the coincident constraint.

        Returns:
            str: The entity token of the point.
        """
        try:
            return nested_getattr(self._obj,'point.entityToken',None)
        except AttributeError as e:
            self.logger.error(f'Error extracting point: {e}\n{traceback.format_exc()}')
            return None

    @property
    def entity(self) -> Optional[str]:
        """Extracts the entity of the coincident constraint.

        Returns:
            str: The entity token of the entity.
        """
        try:
            return nested_getattr(self._obj,'entity.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting entity: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the CoincidentConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'point': self.point,
            'entity': self.entity,
        }
        return {**base_info, **constraint_info}

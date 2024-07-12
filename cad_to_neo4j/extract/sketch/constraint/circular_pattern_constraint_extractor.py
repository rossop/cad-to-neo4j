"""
Circular Pattern Constraint Extractor Module

This module provides an extractor class for extracting information from CircularPatternConstraint objects.

Classes:
    - CircularPatternConstraintExtractor: Extractor for CircularPatternConstraint objects.
"""

from typing import Optional, Dict, Any
import traceback
from adsk.fusion import CircularPatternConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.general_utils import nested_getattr

class CircularPatternConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for CircularPatternConstraint objects."""

    def __init__(self, obj: CircularPatternConstraint):
        """
        Initialise the extractor with the CircularPatternConstraint element.

        Args:
            obj (CircularPatternConstraint): The CircularPatternConstraint object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the CircularPatternConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'entities': self.entities,
            'createdEntities': self.createdEntities,
            'centerPoint': self.centerPoint,
            'quantity': self.quantity,
            'totalAngle': self.totalAngle,
            'isSymmetric': self.isSymmetric,
            'isSuppressed': self.isSuppressed,
        }
        return {**base_info, **constraint_info}

    @property
    def entities(self) -> Optional[list]:
        """Extracts the entities to pattern.

        Returns:
            list: A list of entity tokens of the entities to pattern.
        """
        try:
            return [nested_getattr(entity, 'entityToken', None) for entity in getattr(self._obj, 'entities', [])]
        except AttributeError as e:
            self.logger.error(f'Error extracting entities: {e}\n{traceback.format_exc()}')
            return None

    @property
    def createdEntities(self) -> Optional[list]:
        """Extracts the created entities of the pattern.

        Returns:
            list: A list of entity tokens of the created entities.
        """
        try:
            return [nested_getattr(entity, 'entityToken', None) for entity in getattr(self._obj, 'createdEntities', [])]
        except AttributeError as e:
            self.logger.error(f'Error extracting createdEntities: {e}\n{traceback.format_exc()}')
            return None

    @property
    def centerPoint(self) -> Optional[str]:
        """Extracts the center point of the pattern.

        Returns:
            str: The entity token of the center point.
        """
        try:
            return nested_getattr(self._obj, 'centerPoint.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting centerPoint: {e}\n{traceback.format_exc()}')
            return None

    @property
    def quantity(self) -> Optional[str]:
        """Extracts the quantity parameter of the pattern.

        Returns:
            str: The entity token of the quantity parameter.
        """
        try:
            return nested_getattr(self._obj, 'quantity.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting quantity: {e}\n{traceback.format_exc()}')
            return None

    @property
    def totalAngle(self) -> Optional[str]:
        """Extracts the total angle parameter of the pattern.

        Returns:
            str: The entity token of the total angle parameter.
        """
        try:
            return nested_getattr(self._obj, 'totalAngle.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting totalAngle: {e}\n{traceback.format_exc()}')
            return None

    @property
    def isSymmetric(self) -> Optional[bool]:
        """Extracts the symmetry status of the pattern.

        Returns:
            bool: True if the pattern is symmetric, False otherwise.
        """
        try:
            return getattr(self._obj, 'isSymmetric', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting isSymmetric: {e}\n{traceback.format_exc()}')
            return None

    @property
    def isSuppressed(self) -> Optional[list]:
        """Extracts the suppression status of the pattern instances.

        Returns:
            list: A list of boolean values indicating the suppression status of the pattern instances.
        """
        try:
            return getattr(self._obj, 'isSuppressed', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting isSuppressed: {e}\n{traceback.format_exc()}')
            return None

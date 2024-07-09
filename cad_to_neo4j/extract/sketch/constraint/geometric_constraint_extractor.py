"""
Geometric Constraint Extractor Module

This module provides a base extractor class for geometric constraints.

Classes:
    - GeometricConstraintExtractor: Extractor for GeometricConstraint objects.
"""
from typing import Optional, Dict, Any
from adsk.core import Attributes
from adsk.fusion import GeometricConstraint, Sketch, Occurrence
from ...base_extractor import BaseExtractor
import traceback
from ....utils.general_utils import nested_getattr

__all__ = ['GeometricConstraintExtractor']

class GeometricConstraintExtractor(BaseExtractor):
    """Extractor for extracting detailed information from GeometricConstraint objects."""

    def __init__(self, element: GeometricConstraint):
        """Initialize the extractor with the GeometricConstraint element."""
        super().__init__(element)

    @property
    def is_deletable(self) -> Optional[bool]:
        """Indicates if this constraint is deletable.

        Returns:
            bool: True if the constraint is deletable, False otherwise.
        """
        try:
            return self._obj.isDeletable
        except AttributeError as e:
            self.logger.error(f'Error extracting isDeletable: {e}\n{traceback.format_exc()}')
            return None

    @property
    def parentSketch(self) -> Optional[str]:
        """Extracts the ID of the parent sketch.

        Returns:
            str: The entity token of the parent sketch.
        """
        try:
            return nested_getattr(self._obj,'parentSketch.entityToken',None)
        except AttributeError as e:
            self.logger.error(f'Error extracting parentSketch: {e}\n{traceback.format_exc()}')
            return None
        


    # @property
    # def assembly_context(self) -> Optional[str]:
    #     """Extracts the assembly context of the geometric constraint.

    #     Returns:
    #         str: The entity token of the assembly context.
    #     """
    #     try:
    #         return nested_getattr(self._obj, 'assemblyContext.entityToken', None)
    #     except AttributeError as e:
    #         self.logger.error(f'Error extracting assemblyContext: {e}\n{traceback.format_exc()}')
    #         return None

    # @property
    # def attributes(self) -> Optional[Dict[str, Any]]:
    #     """Extracts the attributes associated with this geometric constraint.

    #     Returns:
    #         dict: A dictionary of attribute names and their values.
    #     """
    #     try:
    #         attributes = {}
    #         for attr in getattr(self._obj,'attributes', []):
    #             attributes[attr.name] = attr.value
    #         return attributes
    #     except AttributeError as e:
    #         self.logger.error(f'Error extracting attributes: {e}\n{traceback.format_exc()}')
    #         return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the GeometricConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'is_deletable': self.is_deletable,
            'parentSketch': self.parentSketch,
            # 'assembly_context': self.assembly_context,
        }
        return {**base_info, **constraint_info}
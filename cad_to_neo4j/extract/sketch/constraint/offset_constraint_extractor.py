"""
Offset Constraint Extractor Module

This module provides an extractor class for extracting information from OffsetConstraint objects.

Classes:
    - OffsetConstraintExtractor: Extractor for OffsetConstraint objects.
"""
from typing import Optional, Dict, Any
import traceback
from adsk.fusion import OffsetConstraint
from .geometric_constraint_extractor import GeometricConstraintExtractor
from ....utils.extraction_utils import nested_getattr

class OffsetConstraintExtractor(GeometricConstraintExtractor):
    """Extractor for OffsetConstraint objects."""

    def __init__(self, obj: OffsetConstraint):
        """
        Initialise the extractor with the OffsetConstraint element.

        Args:
            obj (OffsetConstraint): The OffsetConstraint object to extract information from.
        """
        super().__init__(obj)

    @property
    def parent_curves(self) -> Optional[list]:
        """Extracts the parent curves of the offset constraint.

        Returns:
            list: A list of entity tokens of the parent curves.
        """
        try:
            return [
                getattr(curve, 'entityToken', None) 
                for curve in getattr(self._obj, 'parentCurves', []) 
                if getattr(curve, 'entityToken', None) is not None
            ]
        except AttributeError as e:
            self.logger.error(f'Error extracting parentCurves: {e}\n{traceback.format_exc()}')
            return None

    @property
    def child_curves(self) -> Optional[list]:
        """Extracts the child curves of the offset constraint.

        Returns:
            list: A list of entity tokens of the child curves.
        """
        try:
            return [
                getattr(curve, 'entityToken', None) 
                for curve in getattr(self._obj, 'childCurves', []) 
                if getattr(curve, 'entityToken', None) is not None
            ]
        except AttributeError as e:
            self.logger.error(f'Error extracting childCurves: {e}\n{traceback.format_exc()}')
            return None

    @property
    def distance(self) -> Optional[float]:
        """Extracts the distance of the offset constraint.

        Returns:
            float: The distance of the offset constraint.
        """
        try:
            return getattr(self._obj,'distance', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting distance: {e}\n{traceback.format_exc()}')
            return None

    @property
    def dimension(self) -> Optional[str]:
        """Extracts the dimension controlling the offset distance.

        Returns:
            str: The entity token of the dimension.
        """
        try:
            return nested_getattr(self._obj,'dimension.entityToken', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting dimension: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> Dict[str, Optional[Any]]:
        """Extract all information from the OffsetConstraint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        constraint_info = {
            'parent_curves': self.parent_curves,
            'child_curves': self.child_curves,
            'distance': self.distance,
            'dimension': self.dimension,
        }
        return {**base_info, **constraint_info}

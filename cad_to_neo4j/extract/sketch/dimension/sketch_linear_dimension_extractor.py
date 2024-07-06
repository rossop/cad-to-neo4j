"""
Sketch Linear Dimension Extractor Module

This module provides an extractor class for extracting information from SketchLinearDimension objects.

Classes:
    - SketchLinearDimensionExtractor: Extractor for SketchLinearDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchLinearDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchLinearDimensionExtractor']

class SketchLinearDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchLinearDimension objects."""

    def __init__(self, obj: SketchLinearDimension):
        """
        Initialize the extractor with the SketchLinearDimension element.

        Args:
            obj (SketchLinearDimension): The SketchLinearDimension object to extract information from.
        """
        super().__init__(obj)

    @property
    def entity_one(self) -> Optional[str]:
        """
        Extract the first entity being constrained.

        Returns:
            str: The entity token of the first entity, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'entityOne.entityToken', None)
        except AttributeError:
            return None

    @property
    def entity_two(self) -> Optional[str]:
        """
        Extract the second entity being constrained.

        Returns:
            str: The entity token of the second entity, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'entityTwo.entityToken', None)
        except AttributeError:
            return None

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchLinearDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'entity_one': self.entity_one,
            'entity_two': self.entity_two,
        }

        return {**basic_info, **dimension_info}

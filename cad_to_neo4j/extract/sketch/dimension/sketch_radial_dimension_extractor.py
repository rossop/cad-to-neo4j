"""
Sketch Radial Dimension Extractor Module

This module provides an extractor class for extracting information from SketchRadialDimension objects.

Classes:
    - SketchRadialDimensionExtractor: Extractor for SketchRadialDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchRadialDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchRadialDimensionExtractor']

class SketchRadialDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchRadialDimension objects."""

    def __init__(self, obj: SketchRadialDimension):
        """
        Initialize the extractor with the SketchRadialDimension element.

        Args:
            obj (SketchRadialDimension): The SketchRadialDimension object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchRadialDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'entity': self.entity,
        }

        return {**basic_info, **dimension_info}

    @property
    def entity(self) -> Optional[str]:
        """
        Extract the arc or circle being constrained.

        Returns:
            str: The entity token of the arc or circle, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'entity.entityToken', None)
        except AttributeError:
            return None

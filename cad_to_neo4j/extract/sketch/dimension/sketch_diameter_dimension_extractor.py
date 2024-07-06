"""
Sketch Diameter Dimension Extractor Module

This module provides an extractor class for extracting information from SketchDiameterDimension objects.

Classes:
    - SketchDiameterDimensionExtractor: Extractor for SketchDiameterDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchDiameterDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.general_utils import nested_getattr

__all__ = ['SketchDiameterDimensionExtractor']

class SketchDiameterDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchDiameterDimension objects."""

    def __init__(self, obj: SketchDiameterDimension):
        """
        Initialize the extractor with the SketchDiameterDimension element.

        Args:
            obj (SketchDiameterDimension): The SketchDiameterDimension object to extract information from.
        """
        super().__init__(obj)

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

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchDiameterDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'entity': self.entity,
        }

        return {**basic_info, **dimension_info}

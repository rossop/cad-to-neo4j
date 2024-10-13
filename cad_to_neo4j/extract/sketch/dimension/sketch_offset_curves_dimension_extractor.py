"""
Sketch Offset Curves Dimension Extractor Module

This module provides an extractor class for extracting information from SketchOffsetCurvesDimension objects.

Classes:
    - SketchOffsetCurvesDimensionExtractor: Extractor for SketchOffsetCurvesDimension objects.
"""

from typing import Optional, Dict, Any
from adsk.fusion import SketchOffsetCurvesDimension
from .sketch_dimension_extractor import SketchDimensionExtractor
from ....utils.extraction_utils import nested_getattr

__all__ = ['SketchOffsetCurvesDimensionExtractor']

class SketchOffsetCurvesDimensionExtractor(SketchDimensionExtractor):
    """Extractor for extracting detailed information from SketchOffsetCurvesDimension objects."""

    def __init__(self, obj: SketchOffsetCurvesDimension):
        """
        Initialize the extractor with the SketchOffsetCurvesDimension element.

        Args:
            obj (SketchOffsetCurvesDimension): The SketchOffsetCurvesDimension object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the SketchOffsetCurvesDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'offsetConstraint': self.offsetConstraint,
        }

        return {**basic_info, **dimension_info}

    @property
    def offsetConstraint(self) -> Optional[str]:
        """
        Extract the OffsetConstraint object that defines the curve offset.

        Returns:
            str: The entity token of the OffsetConstraint, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'offsetConstraint.entityToken', None)
        except AttributeError:
            return None

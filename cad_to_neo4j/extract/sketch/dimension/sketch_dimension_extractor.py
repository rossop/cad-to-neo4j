"""
Sketch Dimension Extractor Module

This module provides an extractor class for extracting information from SketchDimension objects.

Classes:
    - SketchDimensionExtractor: Extractor for SketchDimension objects.
"""
from typing import Optional, Dict, Any
from adsk.fusion import SketchDimension
from ...base_extractor import BaseExtractor

__all__ = ['SketchDimensionExtractor']

class SketchDimensionExtractor(BaseExtractor):
    """Extractor for extracting detailed information from SketchDimension objects."""

    def __init__(self, obj: SketchDimension):
        """Initialize the extractor with the SketchDimension element."""
        super().__init__(obj)

    @property
    def dimension_value(self) -> Optional[float]:
        """Extract the value of the sketch dimension."""
        try:
            return None
        except AttributeError:
            return None

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the SketchDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'dimension' : self.dimension_value,
        }

        return {**basic_info, **dimension_info}
"""
Sketch Curve Extractor Module

This module provides an extractor class for extracting information from SketchCurve objects.

Classes:
    - SketchCurveExtractor: Extractor for SketchCurve objects.
"""
from typing import Dict, Any
from adsk.fusion import SketchCurve
from ..base_extractor import BaseExtractor
from .sketch_entity_extractor import SketchEntityExtractor

__all__ = ['SketchCurveExtractor']

class SketchCurveExtractor(SketchEntityExtractor):
    """Extractor for extracting detailed information from SketchCurve objects."""
    
    def __init__(self, obj: SketchCurve) -> None:
        """Initialize the extractor with the SketchCurve element."""
        super().__init__(obj)
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchCurve element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        curve_info = {
        }
        return {**basic_info, **curve_info}

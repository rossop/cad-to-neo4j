"""
Sketch Element Extractor Module

This module provides a base extractor class for extracting information from sketch elements
such as SketchPoints, SketchCurves, and SketchDimensions.

Classes:
    - SketchElementExtractor: Parent class for other sketch entities.
"""

from typing import Optional, List, Dict, Any
from adsk.fusion import SketchEntity, SketchDimension
from ..base_extractor import BaseExtractor

__all__ = ['SketchEntityExtractor']

class SketchEntityExtractor(BaseExtractor):
    """Parent Class for other Sketch Entities"""

    def __init__(self, obj: SketchEntity):
        """Initialize the extractor with the Sketch Elements."""
        super().__init__(obj)

    @property
    def sketchDimensions(self) -> Optional[List[SketchDimension]]:
        """Extracts the Dimensions linked to this Sketch object.
        
        Returns:
            Optional[List[SketchDimension]]: List of Sketch dimensions that are attached to this object.
        """
        try:
            sketchDimensions = getattr(self._obj, 'sketchDimensions', [])
            return [getattr(dim,'entityToken',None) for dim in sketchDimensions]
        except AttributeError:
            return None
    
    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the Sketch element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_element_info = {
            'sketchDimensions': self.sketchDimensions
        }
        return {**basic_info, **sketch_element_info}

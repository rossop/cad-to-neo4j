"""
Sketch Dimension Extractor Module

This module provides an extractor class for extracting information from SketchDimension objects.

Classes:
    - SketchDimensionExtractor: Extractor for SketchDimension objects.
"""
from typing import Optional, Dict, Any
import adsk.fusion
from ...base_extractor import BaseExtractor
from ....utils.extraction_utils import nested_getattr

__all__ = ['SketchDimensionExtractor']


class SketchDimensionExtractor(BaseExtractor):
    """Extractor for extracting detailed information from SketchDimension objects."""

    def __init__(self, obj: adsk.fusion.SketchDimension):
        """Initialize the extractor with the SketchDimension element."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the SketchDimension element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        dimension_info = {
            'dimension': self.dimensionValue,
            'parentSketch': self.parentSketch,
            'associatedModelParameter': self.associatedModelParameter,
        }

        return {**basic_info, **dimension_info}

    @property
    def dimensionValue(self) -> Optional[float]:
        """Extract the value of the sketch dimension."""
        try:
            return getattr(self._obj, 'value', None)
        except AttributeError:
            return None

    @property
    def parentSketch(self) -> Optional[str]:
        """
        Returns the parent sketch.
        """
        try:
            return nested_getattr(self._obj, 'parentSketch.entityToken', None)
        except AttributeError:
            return None

    @property
    def associatedModelParameter(self) -> Optional[str]:
        """
        Returns the entityToken of the ModelParameter associated with this SketchDimension.

        Returns:
            Optional[str]: The entityToken of the associated ModelParameter, if present.
        """
        try:
            # Check if the SketchDimension has an associated ModelParameter
            model_parameter: adsk.fusion.ModelParameter = getattr(self._obj, 'parameter', None)
            if model_parameter:
                return model_parameter.entityToken
            return None
        except AttributeError:
            return None

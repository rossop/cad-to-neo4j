"""
Extractor Factory Module

This module provides a factory function to get the appropriate extractor
based on the type of CAD element.

Functions:
    - get_extractor: Returns the appropriate extractor for the given element.
"""

from adsk.core import Base
from adsk.fusion import Sketch, Feature
from .base_extractor import BaseExtractor
from .sketch_extractor import SketchExtractor
from .feature_extractor import FeatureExtractor

__all__ = ['get_extractor']

EXTRACTORS = {
    'adsk::fusion::Sketch': SketchExtractor,
    'adsk::fusion::ExtrudeFeature': FeatureExtractor, 
}
# TODO generalise for different features

def get_extractor(element: Base) -> BaseExtractor:
    """Get the appropriate extractor for the given CAD element.

    Args:
        element (Base): The CAD element.

    Returns:
        BaseExtractor: The appropriate extractor for the element.
    """
    extractor_class = EXTRACTORS.get(element.objectType, BaseExtractor)
    return extractor_class(element)

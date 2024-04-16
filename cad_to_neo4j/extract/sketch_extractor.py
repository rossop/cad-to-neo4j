"""
Sketch Extractor Module

This module provides an extractor class for extracting information from Sketch objects.

Classes:
    - SketchExtractor: Extractor for Sketch objects.
"""

from adsk.fusion import Sketch
from .base_extractor import BaseExtractor

__all__ = ['SketchExtractor']

class SketchExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Sketch objects."""

    def __init__(self, element: Sketch):
        """Initialize the extractor with the Sketch element."""
        super().__init__(element)

    def extract_all_info(self) -> dict:
        """Extract all information from the Sketch element."""
        info = super().extract_all_info()
        # Add more sketch-specific extraction logic here
        return info

"""
BRep Extractor Module

This module provides an extractor class for extracting information from 
Boundary Representations objects.

Classes:
    - BRepExtractor: Extractor for BRep objects.
"""

import adsk.fusion # TODO standardise this import for 
from .base_extractor import BaseExtractor
from ..utils.logger import log_function

__all__ = ['BRepExtractor']

class BRepExtractor(BaseExtractor):
    """Extractor for BRep data from bodies and features."""
    def __init__(self, obj: adsk.fusion.BRepBody):
        """Initialize the extractor with the Feature element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract BRep data from the body or feature."""
        basic_info = super().extract_info()
        brep_data = {
            **basic_info,
            # 'brep': self.extract_brep_data(),
        }
        return brep_data
    

    

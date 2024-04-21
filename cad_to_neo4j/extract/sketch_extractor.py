"""
Sketch Extractor Module

This module provides an extractor class for extracting information from Sketch objects,
including SketchPoints, SketchCurves, and SketchDimensions.

Classes:
    - SketchExtractor: Extractor for Sketch objects.
    - SketchPointExtractor: Extractor for SketchPoint objects.
    - SketchCurveExtractor: Extractor for SketchCurve objects.
    - SketchDimensionExtractor: Extractor for SketchDimension objects.
"""
from typing import Optional, Dict, List, Any
from adsk.fusion import Sketch, SketchEntity, SketchPoint, SketchCurve, SketchLine, SketchDimension, Profile
from .base_extractor import BaseExtractor
from ..utils.general_utils import nested_getattr

import adsk.core, trace

__all__ = ['SketchExtractor','SketchPointExtractor', 'SketchCurveExtractor', 'SketchDimensionExtractor', 'ProfileExtractor']

class SketchElementExtractor(BaseExtractor):
    """Parent Class for other Sketch Entities"""

    def __init__(self, element: SketchEntity):
        """Initialize the extractor with the Sketch Elements."""
        super().__init__(element)

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
        basic_info =  super().extract_info()
        sketch_element_info = {
            'sketchDimensions': self.sketchDimensions
        }
        return {**basic_info, **sketch_element_info}

class SketchExtractor(SketchElementExtractor):
    """Extractor for extracting detailed information from Sketch objects."""

    def __init__(self, element: Sketch):
        """Initialize the extractor with the Sketch element."""
        super().__init__(element)

    @property
    def timeline_index(self) -> Optional[int]:
        """Extracts the timeline index of the Sketch object.
        
        Returns:
            int: The timeline index of the Sketch object, or None if not available.
        """
        try:
            return nested_getattr(self._obj,'timelineObject.index', None)
        except AttributeError:
            return None
    
    def extract_info(self) -> dict:
        """Extract all information from the Sketch element.
        
        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_info = {
            'timeline_index': self.timeline_index
        }
        return {**basic_info, **sketch_info}


class SketchPointExtractor(SketchElementExtractor):
    """Extractir for extracting information from Sketch Point objects."""

    def __init__(self, element: SketchPoint) -> None:
        """Initialize the extractor with the SketchPoint element."""
        super().__init__(element)

    @property
    def coordinates(self) -> Optional[List[float]]:
        """Extract the coordinates of the sketch point."""
        try:
            return self._obj.geometry.asArray
        except AttributeError:
            return None

    @property
    def connectedEntities(self) -> Optional[List[float]]:
        """Extract the entities connected to the sketch point."""
        try:
            connectedEntities = getattr(self._obj, 'connectedEntities', [])
            if connectedEntities is None:
                connectedEntities = []
            id_tokens = []
            for e in connectedEntities:
                token = getattr(e,'entityToken', None) 
                if token is not None:
                    id_tokens.append(token)
            return id_tokens
        except AttributeError:
            return None
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchPoint element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        point_info = {
            # 'coordinates': self.coordinates,
            'connectedEntities': self.connectedEntities,
        }
        return {**basic_info, **point_info}
    
class SketchCurveExtractor(SketchElementExtractor):
    """Extractor for extracting detailed information from SketchCurve objects."""
    
    def __init__(self, element: SketchCurve) -> None:
        """Initialize the extractor with the SketchCurve element."""
        super().__init__(element)
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchCurve element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        curve_info = {
        }
        return {**basic_info, **curve_info}
    
class SketchLineExtractor(SketchCurveExtractor):
    """Extractor for extracting detailed information from SketchLine objects."""
    
    def __init__(self, element: SketchLine) -> None:
        """Initialize the extractor with the SketchLine element."""
        super().__init__(element)

    @property
    def startSketchPoint(self):
        try:
            return nested_getattr(self._obj, 'startSketchPoint.entityToken', None)
        except AttributeError:
            return None 

    @property
    def endSketchPoint(self):
        try:
            return nested_getattr(self._obj, 'endSketchPoint.entityToken', None)
        except AttributeError:
            return None
    
    def extract_info(self) -> Dict[str,Any]:
        """Extract all information from the SketchLine element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        line_info = {
            'startPoint': self.startSketchPoint,
            'endPoint': self.endSketchPoint,
        }
        return {**basic_info, **line_info}
    
class SketchDimensionExtractor(BaseExtractor):
    """Extractor for extracting detailed information from SketchDimension objects."""

    def __init__(self, element: SketchDimension):
        """Initialize the extractor with the SketchDimension element."""
        super().__init__(element)

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
    

class ProfileExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Profile objects."""

    def __init__(self, element: Profile):
        """Initialize the extractor with the Profile element."""
        super().__init__(element)

    @property
    def _profile_loops(self) -> Optional[List[str]]:
        """Extracts the loops or closed areas within this profile."""
        try:
            loops = getattr(self._obj, 'profileLoops', [])
            return [loop for loop in loops]
        except AttributeError:
            return None
        
    @property
    def profile_curves(self) -> Optional[List[str]]:
        """Extracts the curves within this profile."""
        try:
            id_tokens = []
            for profile_loop in self._profile_loops:
                for profile_curve in getattr(profile_loop, 'profileCurves', []):
                    token = nested_getattr(profile_curve, 'sketchEntity.entityToken', None)  
                    if token is not None:                     
                        id_tokens.append(token)
            return id_tokens
        except AttributeError:
            return None

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the Profile element."""
        basic_info = super().extract_info()
        profile_info = {
            'profile_curves': self.profile_curves,
        }
        # Debug log for properties
        return {**basic_info, **profile_info}
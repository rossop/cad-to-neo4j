# profile_loop_extractor.py
"""
Profile Loop Extractor Module

This module provides an extractor class for extracting information from ProfileLoop objects.

Classes:
    - ProfileLoopExtractor: Extractor for ProfileLoop objects.

Functions:
    - extract_info: Extracts information from the ProfileLoop object and returns it as a dictionary.
    - isOuter: Property to get the outer loop status of the ProfileLoop object.
    - curveInfo: Property to get the information about profile curves in the ProfileLoop object.
"""
import uuid
from typing import Dict, Any, Optional
from adsk.fusion import ProfileLoop
from ...base_extractor import BaseExtractor
from .profile_curve_extractor import ProfileCurveExtractor

class ProfileLoopExtractor(BaseExtractor):
    """
    Extractor for extracting detailed information from ProfileLoop objects.

    This class provides methods to extract various properties from ProfileLoop objects,
    including whether the loop is outer, and details about the profile curves within the loop.

    Attributes:
        element (adsk.fusion.ProfileLoop): The ProfileLoop object to extract data from.
    """
    def __init__(self, obj: ProfileLoop):
        """
        Initialize the extractor with the ProfileLoop element.

        Args:
            obj (adsk.fusion.ProfileLoop): The ProfileLoop object to extract data from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the ProfileLoop element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        loop_info = {
            'isOuter': self.isOuter,
            'profileCurves': None,
            'tempId' : None,
        }

        # Add curveInfo if available
        curve_info = self.curveInfo
        if curve_info is not None:
            loop_info.update(curve_info)

        return {**base_info, **loop_info}

    @property
    def isOuter(self) -> bool:
        """
        Get the outer loop status of the ProfileLoop object.

        Returns:
            bool: True if the loop is an outer loop, False otherwise.
        """
        return getattr(self._obj, 'isOuter', None)

    @property
    def curveInfo(self) -> Optional[Dict[str,Any]]:
        """
        Get the information about profile curves in the ProfileLoop object.

        Returns:
            dict: A dictionary containing profile curve entities and their tempIds.
        """
        try:
            curvesEntities = getattr(self._obj, 'profileCurves', [])
            profileCurves = []
            profileCurveEntities =[]
            for curve in curvesEntities:
                info = ProfileCurveExtractor(curve).extract_info()
                if info['tempId'] is None:
                    tempId = str(uuid.uuid4())
                    info['tempId'] = tempId
                    profileCurves.append(tempId)
                    profileCurveEntities.append(info)
            
            return {
                'profileCurveEntities' : profileCurveEntities,
                'profileCurves' : profileCurves,
            }
        except AttributeError:
            return None
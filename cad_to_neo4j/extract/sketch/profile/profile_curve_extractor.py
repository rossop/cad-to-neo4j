# profile_curve_extractor.py
"""
Profile Curve Extractor Module

This module provides an extractor class for extracting information from ProfileCurve objects.

Classes:
    - ProfileCurveExtractor: Extractor for ProfileCurve objects.

Functions:
    - extract_info: Extracts information from the ProfileCurve object and returns it as a dictionary.
    - geometry_type: Property to get the geometry type of the ProfileCurve object.
    - geometry: Property to get the geometry details (start and end points) of the ProfileCurve object.
    - sketch_entity: Property to get the associated sketch entity token of the ProfileCurve object.
"""
from typing import Dict, Any
from adsk.fusion import ProfileCurve
from ...base_extractor import BaseExtractor

from ....utils.general_utils import nested_getattr

class ProfileCurveExtractor(BaseExtractor):
    """
    Extractor for extracting detailed information from ProfileCurve objects.

    This class provides methods to extract various properties from ProfileCurve objects,
    including geometry type, geometry details, and associated sketch entity token.

    Attributes:
        element (adsk.fusion.ProfileCurve): The ProfileCurve object to extract data from.
    """
    def __init__(self, obj: ProfileCurve):
        """
        Initialise the extractor with the ProfileCurve object.

        Args:
            obj (adsk.fusion.ProfileCurve): The ProfileCurve object to extract data from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the ProfileCurve object.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        base_info = super().extract_info()
        curve_info = {
            'geometryType': self.geometry_type,
            'sketchEntity': self.sketch_entity,
            'tempId' : None,
        }

        # Add geometry information if available
        geometry = self.geometry
        if geometry is not None:
            curve_info.update(geometry)
        return {**curve_info,**base_info}

    @property
    def geometry_type(self) -> str:
        """
        Get the geometry type of the ProfileCurve object.

        Returns:
            str: The geometry type.
        """
        try:
            return getattr(self._obj, 'geometryType', None)
        except:
            return None

    @property
    def geometry(self) -> Dict[str, Any]:
        """
        Get the geometry details of the ProfileCurve object.

        Returns:
            dict: A dictionary containing the start and end points of the geometry.
        """
        geom = getattr(self._obj, 'geometry', None)
        try:
            if geom:
                return {
                    'startPoint': [geom.startPoint.x, geom.startPoint.y, geom.startPoint.z],
                    'endPoint': [geom.endPoint.x, geom.endPoint.y, geom.endPoint.z]
                }
            return {}
        except:
            # TODO deal with different types of curves which will have different types of geometries
            return {}

    @property
    def sketch_entity(self) -> str:
        """
        Get the associated sketch entity token of the ProfileCurve object.

        Returns:
            str: The sketch entity token.
        """
        return nested_getattr(self._obj, 'sketchEntity.entityToken', None)
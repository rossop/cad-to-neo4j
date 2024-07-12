"""
Profile Extractor Module

This module provides an extractor class for extracting information from Profile objects.

Classes:
    - ProfileExtractor: Extractor for Profile objects.
"""
from typing import Optional, Dict, List, Any
from adsk.fusion import Profile
from ..base_extractor import BaseExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['ProfileExtractor']

class ProfileExtractor(BaseExtractor):
    """
    Extractor for extracting detailed information from Profile objects.

    This class provides methods to extract various properties from Profile objects,
    including profile curves, bounding box, area properties, and more.

    Attributes:
        element (adsk.fusion.Profile): The Profile object to extract data from.
    """

    def __init__(self, obj: Profile):
        """
        Initialize the extractor with the Profile element.

        Args:
            obj (adsk.fusion.Profile): The Profile object to extract data from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the Profile element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        profile_info = {
            'profileCurves': self.profileCurves,
            'profileLoops': self.profileLoops,
            'parentSketch': self.parentSketch,
        }

        # Add plane information if available
        areaProperties_info = self.areaProperties
        if areaProperties_info is not None:
            profile_info.update(areaProperties_info)

        # Add plane information if available
        plane_info = self.plane
        if plane_info is not None:
            profile_info.update(plane_info)

        # Add bounding box information if available
        bbbox_info = self.boundingBox
        if bbbox_info is not None:
            profile_info.update(bbbox_info)

        return {**basic_info, **profile_info}

    @property
    def profileLoops(self) -> Optional[List[str]]:
        """
        Extracts the loops or closed areas within this profile, including their identity tokens if available.

        Returns:
            Optional[List[str]]: List of identity tokens for the profile loops.
        """
        try:
            loops = getattr(self._obj, 'profileLoops', [])
            return [getattr(loop, 'entityToken', None) for loop in loops]
        except AttributeError:
            return None
        
    @property
    def profileCurves(self) -> Optional[List[str]]:
        """
        Extracts the curves within this profile.

        Returns:
            Optional[List[str]]: List of entity tokens for the profile curves.
        """
        try:
            entityTokens = []
            for profile_loop in self._profileLoops:
                for profile_curve in getattr(profile_loop, 'profileCurves', []):
                    token = nested_getattr(profile_curve, 'sketchEntity.entityToken', None)  
                    if token is not None:                     
                        entityTokens.append(token)
            return entityTokens
        except AttributeError:
            return None
        
    @property
    def boundingBox(self) -> Optional[Dict[str, List[float]]]:
        """
        Returns the 3D bounding box of the profile in sketch space.

        Returns:
            Optional[Dict[str, List[float]]]: Dictionary with min and max points of the bounding box.
        """
        try:
            bbox = getattr(self._obj, 'boundingBox', None)
            if bbox:
                return {
                    'bbMinPoint': [bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z],
                    'bbMaxPoint': [bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error extracting bounding box: {e}")
            return None

    @property
    def plane(self) -> Optional[Dict[str, Any]]:
        """
        Returns the plane the profile is defined in.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing plane information.
        """
        try:
            plane = getattr(self._obj, 'plane', None)
            if plane:
                return {
                    'origin': [plane.origin.x, plane.origin.y, plane.origin.z],
                    'normal': [plane.normal.x, plane.normal.y, plane.normal.z]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error extracting plane: {e}")
            return None

    @property
    def areaProperties(self) -> Optional[Dict[str, Any]]:
        """
        Calculates the area properties for the profile.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing area properties.
        """
        try:
            area_props = self._obj.areaProperties()
            return {
                'area': area_props.area,
                'perimeter': area_props.perimeter,
                'centroid': [area_props.centroid.x, area_props.centroid.y, area_props.centroid.z]
            }
        except Exception as e:
            self.logger.error(f"Error extracting area properties: {e}")
            return None

    @property
    def parentSketch(self) -> Optional[str]:
        """
        Returns the parent sketch of the profile.

        Returns:
            Optional[str]: Entity token of the parent sketch.
        """
        try:
            parentSketch = getattr(self._obj, 'parentSketch', None)
            return getattr(parentSketch, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting parent sketch: {e}")
            return None

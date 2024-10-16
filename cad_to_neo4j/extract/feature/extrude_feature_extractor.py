"""
Extrude Feature Extractor Module

This module provides an extractor class for extracting information from
ExtrudeFeature objects.

Classes:
    - ExtrudeFeatureExtractor: Extractor for ExtrudeFeature objects.
"""
from typing import Optional, Any, Dict, List

import adsk.fusion
import adsk.core

from .feature_extractor import FeatureExtractor
from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import (
    nested_getattr,
    helper_extraction_error
)

__all__ = ['ExtrudeFeatureExtractor']


class ExtrudeFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from ExtrudeFeature
    objects."""

    def __init__(self, obj: adsk.fusion.ExtrudeFeature):
        """Initialize the extractor with the ExtrudeFeature element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the ExtrudeFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        extrude_info = {
            'profileTokens': self.profile_tokens,
            'bodies': self.bodies,
            'startFaces': self.start_faces,
            'endFaces': self.end_faces,
            'sideFaces': self.side_faces,
            'extent_type': self.extent_type,
            'operation': self.operation,
            'participantBodies': self.participant_bodies,
            'taperAngleOne': self.taper_angle_one_token,
            'taperAngleTwo': self.taper_angle_two_token
        }
        # Add extent one information
        extent_one_info = self.extent_one
        if extent_one_info is not None:
            extrude_info.update(extent_one_info)

        # Add extent two information if available
        extent_two_info = self.extent_two
        if extent_two_info is not None:
            extrude_info.update(extent_two_info)

        extrude_info.update(self.start_extent)
        return {**feature_info, **extrude_info}

    @property
    @helper_extraction_error
    def profile_tokens(self):
        """Extracts the tokens of profiles used by the ExtrudeFeature.

        Returns:
            list: A list of profile tokens used by the ExtrudeFeature.
        """
        profiles = self._obj.profile
        if isinstance(profiles, adsk.core.ObjectCollection):
            profile_list = [profile.entityToken for profile in profiles]
            return profile_list
        return [profiles.entityToken]

    @property
    @helper_extraction_error
    def bodies(self) -> Optional[List[str]]:
        """Extracts the IDs of bodies created or modified by the feature."""
        return self.extract_collection_tokens('bodies', 'entityToken')

    @property
    @helper_extraction_error
    def start_faces(self) -> Optional[List[str]]:
        """Extracts the IDs of start faces created by the feature."""
        return self.extract_collection_tokens('startFaces', 'entityToken')

    @property
    @helper_extraction_error
    def end_faces(self) -> Optional[List[str]]:
        """Extracts the IDs of end faces created by the feature."""
        return self.extract_collection_tokens('endFaces', 'entityToken')

    @property
    @helper_extraction_error
    def side_faces(self) -> Optional[List[str]]:
        """Extracts the IDs of side faces created by the feature."""
        return self.extract_collection_tokens('sideFaces', 'entityToken')

    @property
    @helper_extraction_error
    def start_extent(self) -> Dict[str, Any]:
        """Extracts the start extent definition used by the feature."""
        start_extent_info = {}
        start_extent_type = self.get_first_valid_attribute([
            'startExtent.profilePlane',
            'startExtent.profilePlaneWithOffset',
            'startExtent.entity'
        ])

        if start_extent_type:
            if isinstance(start_extent_type, adsk.core.Plane):
                start_extent_info['start_extent_normal'] = [
                    nested_getattr(
                        self._obj, 'startExtent.profilePlane.normal.x', None),
                    nested_getattr(
                        self._obj, 'startExtent.profilePlane.normal.y', None),
                    nested_getattr(
                        self._obj, 'startExtent.profilePlane.normal.z', None)
                ]
                start_extent_info['start_extent_origin'] = [
                    nested_getattr(
                        self._obj, 'startExtent.profilePlane.origin.x', None),
                    nested_getattr(
                        self._obj, 'startExtent.profilePlane.origin.y', None),
                    nested_getattr(
                        self._obj, 'startExtent.profilePlane.origin.z', None)
                ]
            elif isinstance(
                    start_extent_type,
                    adsk.fusion.ProfilePlaneWithOffsetStartDefinition):
                start_extent_info['start_extent_offset'] = nested_getattr(
                    self._obj, f'{start_extent_type}.offset', None)
            elif isinstance(
                    start_extent_type,
                    adsk.fusion.Entity):
                start_extent_info['start_extent_entity_id'] = nested_getattr(
                    self._obj, f'{start_extent_type}.entityToken', None)

        return start_extent_info

    @property
    @helper_extraction_error
    def extent_type(self) -> Optional[str]:
        """Extracts the direction of the extrusion."""
        one_side_feature_extent_type: int = 0
        two_sides_feature_extent_type: int = 1
        symmetric_feature_extent_type: int = 2

        direction_value: int = self._obj.extentType
        if direction_value == one_side_feature_extent_type:
            return 'One Sided'
        elif direction_value == two_sides_feature_extent_type:
            return 'Two Sided'
        elif direction_value == symmetric_feature_extent_type:
            return 'Symmetric'
        else:
            return 'Unknown'

    def extract_extent_info(self,
                            extent_root: Any,
                            prefix: str) -> Optional[Dict[str, Any]]:
        """Extracts the extent definition information.

        Args:
            extent_root (Any): The extent definition object.
            prefix (str): The prefix to add to the keys in the returned
                dictionary.

        Returns:
            dict: A dictionary containing the extracted extent information.
        """
        if extent_root is not None:
            extent_info = {
                f'{prefix}Type': type(extent_root).__name__,
                f'{prefix}TaperAngleValue': nested_getattr(
                    extent_root, 'taperAngle.value', None),
                f'{prefix}TaperAngleToken': nested_getattr(
                    extent_root, 'taperAngle.entityToken', None),
                f'{prefix}IsPositiveDirection': getattr(
                    extent_root, 'isPositiveDirection', None),
            }

            # Handle DistanceExtentDefinition
            if isinstance(extent_root, adsk.fusion.DistanceExtentDefinition):
                extent_info[f'{prefix}DistanceValue'] = \
                    nested_getattr(extent_root, 'distance.value', None)
                extent_info[f'{prefix}DistanceToken'] = \
                    nested_getattr(extent_root, 'distance.entityToken', None)

            # Handle ThroughAllExtentDefinition
            elif isinstance(
                    extent_root, adsk.fusion.ThroughAllExtentDefinition):
                extent_info[f'{prefix}DistanceValue'] = 'Through All'

            # Handle ToEntityExtentDefinition
            elif isinstance(extent_root, adsk.fusion.ToEntityExtentDefinition):
                extent_info[f'{prefix}OffsetValue'] = \
                    nested_getattr(extent_root, 'distance.value', None)
                extent_info[f'{prefix}OffsetToken'] = \
                    nested_getattr(extent_root, 'distance.entityToken', None)
                extent_info[f'{prefix}EntityToken'] = \
                    nested_getattr(extent_root, 'entity.entityToken', None)

            return extent_info

        return None

    @property
    @helper_extraction_error
    def extent_one(self) -> Optional[Dict[str, Any]]:
        """Extracts the extent one definition used by the feature."""
        extent_one_root = getattr(self._obj, 'extentOne', None)
        return self.extract_extent_info(extent_one_root, 'extentOne')

    @property
    @helper_extraction_error
    def extent_two(self) -> Optional[Dict[str, Any]]:
        """Extracts the extent two definition used by the feature."""
        extent_two_root = getattr(self._obj, 'extentTwo', None)
        return self.extract_extent_info(extent_two_root, 'extentTwo')

    @property
    @helper_extraction_error
    def operation(self) -> Optional[str]:
        """Extracts the type of operation performed by the extrusion."""
        operation_mapping = {
            0: 'JoinFeatureOperation',
            1: 'CutFeatureOperation',
            2: 'IntersectFeatureOperation',
            3: 'NewBodyFeatureOperation',
            4: 'NewComponentFeatureOperation'
        }

        operation_val = getattr(self._obj, 'operation', None)
        return operation_mapping[operation_val] if operation_val else None

    @property
    @helper_extraction_error
    def participant_bodies(self) -> Optional[List[str]]:
        """Extracts the list of bodies that will participate in the feature
        when the operation is a cut or intersection."""
        self.roll_timeline_to_before_feature()
        participant_bodies = getattr(self._obj, 'participantBodies', [])
        ids = [body.entityToken for body in participant_bodies]
        self.roll_timeline_to_after_feature()
        return ids

    @property
    @helper_extraction_error
    def taper_angle_one_token(self) -> Optional[str]:
        """
        Extracts the entity token for the parameter controlling the taper angle
        for side one of the extrusion.
        """
        taper_angle_one = self._obj.taperAngleOne
        if taper_angle_one:
            return taper_angle_one.entityToken
        return None

    @property
    @helper_extraction_error
    def taper_angle_two_token(self) -> Optional[str]:
        """
        Extracts the entity token for the parameter controlling the taper angle
        for side two of the extrusion.
        """
        taper_angle_two = self._obj.taperAngleTwo
        if taper_angle_two:
            return taper_angle_two.entityToken
        return None

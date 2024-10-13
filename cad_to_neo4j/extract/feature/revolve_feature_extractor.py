"""
Revolve Feature Extractor Module

This module provides an extractor class for extracting information from
RevolveFeature objects.

Classes:
    - RevolveFeatureExtractor: Extractor for RevolveFeature objects.
"""
from typing import Optional, Any, Dict, List

import adsk.core
import adsk.fusion

from .feature_extractor import FeatureExtractor

from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error


__all__ = ['RevolveFeatureExtractor']


class RevolveFeatureExtractor(FeatureExtractor):
    """
    Extractor for extracting detailed information from RevolveFeature objects.
    """

    def __init__(self, obj: adsk.fusion.RevolveFeature):
        """Initialize the extractor with the RevolveFeature element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the RevolveFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        revolve_info = {
            'profileTokens': self.profile_tokens,
            'axisToken': self.axis_token,
            'isSolid': self.is_solid,
            'operation': self.operation,
            'participantBodies': self.participant_bodies,
        }

        # Add extent one information
        extent_one_info: Dict[str, Any] = self.extent_one
        if extent_one_info is not None:
            revolve_info.update(extent_one_info)

        # Add extent two information if available
        extent_two_info: Dict[str, Any] = self.extent_two
        if extent_two_info is not None:
            revolve_info.update(extent_two_info)

        return {**feature_info, **revolve_info}

    @property
    @helper_extraction_error
    def profile_tokens(self):
        """Extracts the tokens of profiles used by the RevolveFeature.

        Returns:
            list: A list of profile tokens used by the RevolveFeature.
        """
        profiles = self._obj.profile
        if isinstance(profiles, adsk.core.ObjectCollection):
            return [profile.entityToken for profile in profiles]
        return [profiles.entityToken]

    @property
    @helper_extraction_error
    def axis_token(self):
        """Extracts the token of the axis used by the RevolveFeature.

        Returns:
            str: The token of the axis used by the RevolveFeature.
        """
        return nested_getattr(self._obj, 'axis.entityToken', None)

    @property
    @helper_extraction_error
    def is_solid(self) -> bool:
        """Extracts whether the revolve feature is a solid.

        Returns:
            bool: True if the revolve feature is solid, False otherwise.
        """
        return getattr(self._obj, 'isSolid', None)

    @property
    @helper_extraction_error
    def operation(self) -> Optional[str]:
        """Extracts the type of operation performed by the revolve.

        Returns:
            str: The type of operation.
        """
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
        """
        Extracts the list of bodies that will participate in the feature
        when the operation is a cut or intersection.
        """
        self.roll_timeline_to_before_feature()
        participant_bodies = getattr(self._obj, 'participantBodies', [])
        ids = [body.entityToken for body in participant_bodies]
        self.roll_timeline_to_after_feature()
        return ids

    def extract_extent_info(
            self, extent_root: Any, prefix: str) -> Optional[Dict[str, Any]]:
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
                f'{prefix}Angle': nested_getattr(
                    extent_root, 'angle.valueValue', None),
                f'{prefix}AngleToken': nested_getattr(
                    extent_root, 'angle.entityToken', None),
                f'{prefix}IsSymmetric': nested_getattr(
                    extent_root, 'isSymmetric', None)
            }
            if isinstance(extent_root, adsk.fusion.DistanceExtentDefinition):
                extent_info[f'{prefix}DistanceValue'] = \
                    nested_getattr(extent_root, 'distance.value', None)
                extent_info[f'{prefix}DistanceToken'] = \
                    nested_getattr(extent_root, 'distance.entityToken', None)
            elif isinstance(extent_root, adsk.fusion.ToEntityExtentDefinition):
                extent_info[f'{prefix}EntityToken'] =\
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

"""
Revolve Feature Extractor Module

This module provides an extractor class for extracting information from RevolveFeature objects.

Classes:
    - RevolveFeatureExtractor: Extractor for RevolveFeature objects.
"""
from typing import Optional, Any, Dict, List
from adsk.core import ObjectCollection
from adsk.fusion import RevolveFeature, DistanceExtentDefinition, ToEntityExtentDefinition
import traceback
from .feature_extractor import FeatureExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['RevolveFeatureExtractor']

class RevolveFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from RevolveFeature objects."""

    def __init__(self, obj: RevolveFeature):
        """Initialize the extractor with the RevolveFeature element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the RevolveFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        revolve_info = {
            'profileTokens': self.profileTokens,
            'axisToken': self.axisToken,
            'isSolid': self.isSolid,
            'operation': self.operation,
            'participantBodies': self.participantBodies,
        }

        # Add extent one information
        extentOne_info = self.extentOne
        if extentOne_info is not None:
            revolve_info.update(extentOne_info)

        # Add extent two information if available
        extentTwo_info = self.extentTwo
        if extentTwo_info is not None:
            revolve_info.update(extentTwo_info)

        return {**feature_info, **revolve_info}

    @property
    def profileTokens(self):
        """Extracts the tokens of profiles used by the RevolveFeature.

        Returns:
            list: A list of profile tokens used by the RevolveFeature.
        """
        try:
            profiles = self._obj.profile
            if isinstance(profiles, ObjectCollection):
                return [profile.entityToken for profile in profiles]
            return [profiles.entityToken]
        except AttributeError:
            return []

    @property
    def axisToken(self):
        """Extracts the token of the axis used by the RevolveFeature.

        Returns:
            str: The token of the axis used by the RevolveFeature.
        """
        try:
            return nested_getattr(self._obj, 'axis.entityToken', None)
        except AttributeError:
            return None

    @property
    def isSolid(self) -> bool:
        """Extracts whether the revolve feature is a solid.

        Returns:
            bool: True if the revolve feature is solid, False otherwise.
        """
        try:
            return nested_getattr(self._obj, 'isSolid.entityToken', None)
        except AttributeError:
            return False

    @property
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

        try:
            operation_val = getattr(self._obj, 'operation', None)
            return operation_mapping[operation_val] if operation_val else None
        except AttributeError as e:
            self.logger.error(f'Error extracting operation: {e}\n{traceback.format_exc()}')
            return None

    @property
    def participantBodies(self) -> Optional[List[str]]:
        """Extracts the list of bodies that will participate in the feature when the operation is a cut or intersection."""
        try:
            self.roll_timeline_to_before_feature()
            participantBodies = getattr(self._obj, 'participantBodies', [])
            ids = [body.entityToken for body in participantBodies]
            self.roll_timeline_to_after_feature()
            return ids
        except AttributeError as e:
            self.logger.error(f'Error extracting participant bodies: {e}\n{traceback.format_exc()}')
            return None

    def extract_extent_info(self, extent_root: Any, prefix: str) -> Optional[Dict[str, Any]]:
        """Extracts the extent definition information.

        Args:
            extent_root (Any): The extent definition object.
            prefix (str): The prefix to add to the keys in the returned dictionary.

        Returns:
            dict: A dictionary containing the extracted extent information.
        """
        try:
            if extent_root is not None:
                extent_info = {
                    f'{prefix}_type': type(extent_root).__name__,
                    f'{prefix}_angle': nested_getattr(extent_root, 'angle.value', None),
                    f'{prefix}_isSymmetric': nested_getattr(extent_root, 'isSymmetric', None)
                }
                if isinstance(extent_root, DistanceExtentDefinition):
                    extent_info[f'{prefix}_distance'] = nested_getattr(extent_root, 'distance.value', None)
                elif isinstance(extent_root, ToEntityExtentDefinition):
                    extent_info[f'{prefix}_object_id'] = nested_getattr(extent_root, 'entity.entityToken', None)

                return extent_info

            return None
        except AttributeError as e:
            self.logger.error(f'Error extracting extent info: {e}\n{traceback.format_exc()}')
            return None

    @property
    def extentOne(self) -> Optional[Dict[str, Any]]:
        """Extracts the extent one definition used by the feature."""
        extentOne_root = getattr(self._obj, 'extentOne', None)
        return self.extract_extent_info(extentOne_root, 'extentOne')

    @property
    def extentTwo(self) -> Optional[Dict[str, Any]]:
        """Extracts the extent two definition used by the feature."""
        extentTwo_root = getattr(self._obj, 'extentTwo', None)
        return self.extract_extent_info(extentTwo_root, 'extentTwo')
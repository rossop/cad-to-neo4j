"""
Extrude Feature Extractor Module

This module provides an extractor class for extracting information from ExtrudeFeature objects.

Classes:
    - ExtrudeFeatureExtractor: Extractor for ExtrudeFeature objects.
"""
from typing import Optional, Any, Dict, List
import adsk.fusion
import adsk.core, traceback
from .feature_extractor import FeatureExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['ExtrudeFeatureExtractor']

class ExtrudeFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from ExtrudeFeature objects."""

    def __init__(self, obj: adsk.fusion.ExtrudeFeature):
        """Initialize the extractor with the ExtrudeFeature element."""
        super().__init__(obj)

    @property
    def profile_tokens(self):
        """Extracts the tokens of profiles used by the ExtrudeFeature.

        Returns:
            list: A list of profile tokens used by the ExtrudeFeature.
        """
        try:
            profiles = self._obj.profile
            if isinstance(profiles, adsk.core.ObjectCollection):
                return [profile.entityToken for profile in profiles]
            return [profiles.entityToken]
        except AttributeError:
            return []

    @property
    def bodies(self) -> Optional[List[str]]:
        """Extracts the IDs of bodies created or modified by the feature."""
        try:
            return self.extract_ids('bodies', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting bodies: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def start_faces(self) -> Optional[List[str]]:
        """Extracts the IDs of start faces created by the feature."""
        try:
            return self.extract_ids('startFaces', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting start faces: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def end_faces(self) -> Optional[List[str]]:
        """Extracts the IDs of end faces created by the feature."""
        try:
            return self.extract_ids('endFaces', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting end faces: {e}\n{traceback.format_exc()}')
            return None
        
    @property
    def side_faces(self) -> Optional[List[str]]:
        """Extracts the IDs of side faces created by the feature."""
        try:
            return self.extract_ids('sideFaces', 'entityToken')
        except AttributeError as e:
            self.logger.error(f'Error extracting side faces: {e}\n{traceback.format_exc()}')
            return None
        
    @property
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
                    nested_getattr(self._obj, f'startExtent.profilePlane.normal.x', None),
                    nested_getattr(self._obj, f'startExtent.profilePlane.normal.y', None),
                    nested_getattr(self._obj, f'startExtent.profilePlane.normal.z', None)
                ]
                start_extent_info['start_extent_origin'] = [
                    nested_getattr(self._obj, f'startExtent.profilePlane.origin.x', None),
                    nested_getattr(self._obj, f'startExtent.profilePlane.origin.y', None),
                    nested_getattr(self._obj, f'startExtent.profilePlane.origin.z', None)
                ]
            elif isinstance(start_extent_type, adsk.fusion.ProfilePlaneWithOffsetStartDefinition):
                start_extent_info['start_extent_offset'] = nested_getattr(self._obj, f'{start_extent_type}.offset', None)
            elif isinstance(start_extent_type, adsk.fusion.Entity):
                start_extent_info['start_extent_entity_id'] = nested_getattr(self._obj, f'{start_extent_type}.entityToken', None)

        return start_extent_info
    
    @property
    def extent_type(self) -> Optional[str]:
        """Extracts the direction of the extrusion.""" # TODO make this consistent
        OneSideFeatureExtentType = 0
        TwoSidesFeatureExtentType = 1
        SymmetricFeatureExtentType = 2
        try:
            direction_value = self._obj.extentType
            if direction_value == OneSideFeatureExtentType:
                return 'One Sided'
            elif direction_value == TwoSidesFeatureExtentType:
                return 'Two Sided'
            elif direction_value == SymmetricFeatureExtentType:
                return 'Symmetric'
            else:
                return 'Unknown'
        except AttributeError as e:
            self.logger.error(f'Error extracting extent one: {e}\n{traceback.format_exc()}')
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
                    f'{prefix}_taper_angle': nested_getattr(extent_root, 'taperAngle.value', None),
                    f'{prefix}_is_positive_direction': getattr(extent_root, 'isPositiveDirection', None),
                }
                if isinstance(extent_root, adsk.fusion.DistanceExtentDefinition):
                    extent_info[f'{prefix}_distance'] = nested_getattr(extent_root, 'distance.value', None)
                elif isinstance(extent_root, adsk.fusion.ThroughAllExtentDefinition):
                    extent_info[f'{prefix}_distance'] = 'Through All'
                elif isinstance(extent_root, adsk.fusion.ToEntityExtentDefinition):
                    extent_info[f'{prefix}_offset'] = nested_getattr(extent_root, 'distance.value', None)
                    extent_info[f'{prefix}_object_id'] = nested_getattr(extent_root, 'entity.entityToken', None)

                return extent_info

            return None
        except AttributeError as e:
            self.logger.error(f'Error extracting extent info: {e}\n{traceback.format_exc()}')
            return None

    @property
    def extent_one(self) -> Optional[Dict[str, Any]]:
        """Extracts the extent one definition used by the feature."""
        extent_one_root = getattr(self._obj, 'extentOne', None)
        return self.extract_extent_info(extent_one_root, 'extentOne')

    @property
    def extent_two(self) -> Optional[Dict[str, Any]]:
        """Extracts the extent two definition used by the feature."""
        extent_two_root = getattr(self._obj, 'extentTwo', None)
        return self.extract_extent_info(extent_two_root, 'extentTwo')
    
    @property
    def operation(self) -> Optional[str]:
        """Extracts the type of operation performed by the extrusion."""
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
    def participant_bodies(self) -> Optional[List[str]]:
        """Extracts the list of bodies that will participate in the feature when the operation is a cut or intersection."""
        try:
            self.roll_timeline_to_before_feature()
            participant_bodies = getattr(self._obj, 'participantBodies', [])
            ids = [body.entityToken for body in participant_bodies]
            self.roll_timeline_to_after_feature()
            return ids
        except AttributeError as e:
            self.logger.error(f'Error extracting participant bodies: {e}\n{traceback.format_exc()}')
            return None
            
    def extract_info(self) -> dict:
        """Extract all information from the ExtrudeFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        extrude_info = {
            'profile_tokens': self.profile_tokens,
            'bodies': self.bodies,
            'start_faces': self.start_faces,
            'end_faces': self.end_faces,
            'side_faces': self.side_faces,
            'extent_type': self.extent_type,
            'operation': self.operation,
            'participant_bodies': self.participant_bodies,
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

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
    """Extractor for extracting detailed information from Profile objects."""

    def __init__(self, obj: Profile):
        """Initialize the extractor with the Profile element."""
        super().__init__(obj)

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
        return {**basic_info, **profile_info}

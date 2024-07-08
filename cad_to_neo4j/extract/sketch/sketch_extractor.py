"""
Sketch Extractor Module

This module provides an extractor class for extracting information from Sketch objects,
including SketchPoints, SketchCurves, and SketchDimensions.

Classes:
    - SketchExtractor: Extractor for Sketch objects.
"""
from typing import Optional, Dict, List, Any
from adsk.fusion import Sketch
from ..base_extractor import BaseExtractor
from ...utils.general_utils import nested_getattr
from .sketch_entity_extractor import SketchEntityExtractor
import adsk.core, traceback

__all__ = ['SketchExtractor']
class SketchExtractor(SketchEntityExtractor):
    """Extractor for extracting detailed information from Sketch objects."""
    '''
    REFACTOR: should the following be extracted here instead? 
        - sketchPoints
        - sketchCurves 
        - sketchDimensions
        - geometricConstraints
        - profiles
    It would use self.extract_ids(str)

    FEAT: use getattr(self._obj, 'revisionId', None) for observer
    '''

    def __init__(self, obj: Sketch):
        """Initialize the extractor with the Sketch object."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the Sketch object.
        
        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_info = {
            'timeline_index': self.timeline_index,
            'reference_plane_entity_token': self.reference_plane_entity_token,
            'name': self.name,
            # 'transform': self.transform, # AttributeError: 'Matrix3D' object has no attribute 'getAsArray'
            'is_parametric': self.is_parametric,
            'is_visible': self.is_visible,
            'are_dimensions_shown': self.are_dimensions_shown,
            'are_profiles_shown': self.are_profiles_shown,
            'origin': self.origin,
            'x_direction': self.x_direction,
            'y_direction': self.y_direction,
            # 'bounding_box': self.bounding_box, # change to vector or use update
            'origin_point': self.origin_point,
            'is_fully_constrained': self.is_fully_constrained,
            'base_or_form_feature': self.base_or_form_feature,
            'health_state': self.health_state,
            'error_or_warning_message': self.error_or_warning_message,
            # 'sketch_points': self.sketch_points,
            # 'sketch_curves': self.sketch_curves,
            # 'sketch_dimensions': self.sketch_dimensions,
            # 'geometric_constraints': self.geometric_constraints,
            # 'profiles': self.profiles,
        }
        return {**basic_info, **sketch_info}
    
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
        
    @property
    def reference_plane_entity_token(self) -> Optional[str]:
        """
        Extracts the entity token of the face or plane the sketch is built on.

        This method checks for the referencePlane attribute of the Sketch object,
        which provides information about the plane or face the sketch is created on.
        If the attribute exists, it returns the entity token of the reference plane.

        Returns:
            Optional[str]: The entity token of the reference plane, or None if not available.
        """
        if hasattr(self._obj, 'referencePlane'):
            return nested_getattr(self._obj, 'referencePlane.entityToken', None)
        return None
    
    @property
    def transform(self) -> Optional[List[float]]:
        """Extracts the transform of the Sketch object.

        Returns:
            List[float]: The transform of the Sketch object.
        """
        try:
            transform = nested_getattr(self._obj, 'transform', None)
            if transform:
                return [
                    transform.asArray()[0],  # 'm11'
                    transform.asArray()[1],  # 'm12'
                    transform.asArray()[2],  # 'm13'
                    transform.asArray()[3],  # 'm14'
                    transform.asArray()[4],  # 'm21'
                    transform.asArray()[5],  # 'm22'
                    transform.asArray()[6],  # 'm23'
                    transform.asArray()[7],  # 'm24'
                    transform.asArray()[8],  # 'm31'
                    transform.asArray()[9],  # 'm32'
                    transform.asArray()[10], # 'm33'
                    transform.asArray()[11], # 'm34'
                    transform.asArray()[12], # 'm41'
                    transform.asArray()[13], # 'm42'
                    transform.asArray()[14], # 'm43'
                    transform.asArray()[15], # 'm44'
                ]
            return None
        except AttributeError as e:
            self.logger.error(f'Error extracting transform matrix: {e}\n{traceback.format_exc()}')
            return None
    
    @property
    def is_parametric(self) -> Optional[bool]:
        """Extracts the parametric status of the Sketch object.

        Returns:
            bool: The parametric status of the Sketch object.
        """
        return getattr(self._obj, 'isParametric', None)  
    
    @property
    def is_visible(self) -> Optional[bool]:
        """Extracts the visibility status of the Sketch object.

        Returns:
            bool: The visibility status of the Sketch object.
        """
        return getattr(self._obj, 'isVisible', None)
    
    @property
    def are_dimensions_shown(self) -> Optional[bool]:
        """Extracts the dimensions shown status of the Sketch object.

        Returns:
            bool: The dimensions shown status of the Sketch object.
        """
        return getattr(self._obj, 'areDimensionsShown', None)
    
    @property
    def are_profiles_shown(self) -> Optional[bool]:
        """Extracts the profiles shown status of the Sketch object.

        Returns:
            bool: The profiles shown status of the Sketch object.
        """
        return getattr(self._obj, 'areProfilesShown', None)
    
    @property
    def origin(self) -> Optional[List[float]]:
        """Extracts the origin of the Sketch object.

        Returns:
            List[float]: The origin of the Sketch object.
        """
        origin = nested_getattr(self._obj, 'origin', None)
        if origin:
            return [
                origin.x, # 'x'
                origin.y, # 'y'
                origin.z, # 'z'
            ]
        return None
    
    @property
    def x_direction(self) -> Optional[List[float]]:
        """Extracts the X direction of the Sketch object.

        Returns:
            List[float]: The X direction of the Sketch object.
        """
        x_direction = nested_getattr(self._obj, 'xDirection', None)
        if x_direction:
            return [
                x_direction.x, # 'x'
                x_direction.y, # 'y'
                x_direction.z, # 'z'
            ]
        return None

    @property
    def y_direction(self) -> Optional[List[float]]:
        """Extracts the Y direction of the Sketch object.

        Returns:
            List[float]: The Y direction of the Sketch object.
        """
        y_direction = nested_getattr(self._obj, 'yDirection', None)
        if y_direction:
            return [
                y_direction.x, # 'x'
                y_direction.y, # 'y'
                y_direction.z, # 'z'
            ]
        return None

    @property
    def bounding_box(self) -> Optional[Dict[str, float]]:
        """Extracts the bounding box of the Sketch object.

        Returns:
            Dict[str, float]: The bounding box of the Sketch object.
        """
        bounding_box = nested_getattr(self._obj, 'boundingBox', None)
        if bounding_box:
            return {
                'min_x': bounding_box.minPoint.x,
                'min_y': bounding_box.minPoint.y,
                'min_z': bounding_box.minPoint.z,
                'max_x': bounding_box.maxPoint.x,
                'max_y': bounding_box.maxPoint.y,
                'max_z': bounding_box.maxPoint.z
            }
        return None
    
    @property
    def origin_point(self) -> Optional[str]:
        """Extracts the origin point of the Sketch object.

        Returns:
            str: The origin point of the Sketch object.
        """
        return nested_getattr(self._obj, 'originPoint.entityToken', None)
    
    @property
    def is_fully_constrained(self) -> Optional[bool]:
        """Extracts the fully constrained status of the Sketch object.

        Returns:
            bool: The fully constrained status of the Sketch object.
        """
        return getattr(self._obj, 'isFullyConstrained', None)
    
    @property
    def base_or_form_feature(self) -> Optional[str]:
        """Extracts the base or form feature of the Sketch object.

        Returns:
            str: The base or form feature of the Sketch object.
        """
        return nested_getattr(self._obj, 'baseOrFormFeature.entityToken', None)
    
    @property
    def health_state(self) -> Optional[str]:
        """Extracts the health state of the Sketch object.

        Returns:
            str: The health state of the Sketch object.
        """
        return nested_getattr(self._obj, 'healthState', None)

    @property
    def error_or_warning_message(self) -> Optional[str]:
        """Extracts the error or warning message of the Sketch object.

        Returns:
            str: The error or warning message of the Sketch object.
        """
        return getattr(self._obj, 'errorOrWarningMessage', None)
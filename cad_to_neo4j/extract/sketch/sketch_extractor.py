"""
Sketch Extractor Module

This module provides an extractor class for extracting information from Sketch
objects, including SketchPoints, SketchCurves, and SketchDimensions.

Classes:
    - SketchExtractor: Extractor for Sketch objects.
"""
from typing import Optional, Dict, List, Any

import adsk.core
import adsk.fusion

from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error
from .sketch_entity_extractor import SketchEntityExtractor

__all__ = ['SketchExtractor']


class SketchExtractor(SketchEntityExtractor):
    """Extractor for extracting detailed information from Sketch objects."""

    def __init__(self, obj: adsk.fusion.Sketch):
        """Initialize the extractor with the Sketch object."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the Sketch object.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_info = {
            'timelineIndex': self.timeline_index,
            'reference_plane_entity_token': self.reference_plane_entity_token,
            'name': self.name,
            'isParametric': self.is_parametric,
            'isVisible': self.is_visible,
            'are_dimensions_shown': self.are_dimensions_shown,
            'are_profiles_shown': self.are_profiles_shown,
            'origin': self.origin,
            'x_direction': self.x_direction,
            'y_direction': self.y_direction,
            'origin_point': self.origin_point,
            'is_fully_constrained': self.is_fully_constrained,
            'base_or_form_feature': self.base_or_form_feature,
            'healthState': self.health_state,
            'errorOrWarningMessage': self.error_or_warning_message,
            'parentComponent': self.parent_component,
            # 'transform': self.transform, # AttributeError: 'Matrix3D' object
            # has no attribute 'getAsArray'
        }

        # Add bounding box information if available
        bbbox = self.bounding_box
        if bbbox is not None:
            sketch_info.update(bbbox)

        return {**basic_info, **sketch_info}

    @property
    @helper_extraction_error
    def timeline_index(self) -> Optional[int]:
        """Extracts the timeline index of the Sketch object.

        Returns:
            int: The timeline index of the Sketch object, or None if not
                available.
        """
        return nested_getattr(self._obj, 'timelineObject.index', None)

    @property
    @helper_extraction_error
    def reference_plane_entity_token(self) -> Optional[str]:
        """
        Extracts the entity token of the face or plane the sketch is built on.

        This method checks for the referencePlane attribute of the Sketch
        object, which provides information about the plane or face the sketch
        is created on. If the attribute exists, it returns the entity token of
        the reference plane.

        Returns:
            Optional[str]: The entity token of the reference plane, or None if
                not available.
        """
        if hasattr(self._obj, 'referencePlane'):
            return nested_getattr(
                self._obj, 'referencePlane.entityToken', None)

    @property
    @helper_extraction_error
    def transform(self) -> Optional[List[float]]:
        """Extracts the transform of the Sketch object.

        Returns:
            List[float]: The transform of the Sketch object.
        """
        transform = nested_getattr(self._obj, 'transform', None)
        if transform:
            return [
                transform.asArray()[0],   # 'm11'
                transform.asArray()[1],   # 'm12'
                transform.asArray()[2],   # 'm13'
                transform.asArray()[3],   # 'm14'
                transform.asArray()[4],   # 'm21'
                transform.asArray()[5],   # 'm22'
                transform.asArray()[6],   # 'm23'
                transform.asArray()[7],   # 'm24'
                transform.asArray()[8],   # 'm31'
                transform.asArray()[9],   # 'm32'
                transform.asArray()[10],  # 'm33'
                transform.asArray()[11],  # 'm34'
                transform.asArray()[12],  # 'm41'
                transform.asArray()[13],  # 'm42'
                transform.asArray()[14],  # 'm43'
                transform.asArray()[15],  # 'm44'
            ]
        return None

    @property
    @helper_extraction_error
    def is_parametric(self) -> Optional[bool]:
        """Extracts the parametric status of the Sketch object.

        Returns:
            bool: The parametric status of the Sketch object.
        """
        return getattr(self._obj, 'isParametric', None)

    @property
    @helper_extraction_error
    def is_visible(self) -> Optional[bool]:
        """Extracts the visibility status of the Sketch object.

        Returns:
            bool: The visibility status of the Sketch object.
        """
        return getattr(self._obj, 'isVisible', None)

    @property
    @helper_extraction_error
    def are_dimensions_shown(self) -> Optional[bool]:
        """Extracts the dimensions shown status of the Sketch object.

        Returns:
            bool: The dimensions shown status of the Sketch object.
        """
        return getattr(self._obj, 'areDimensionsShown', None)

    @property
    @helper_extraction_error
    def are_profiles_shown(self) -> Optional[bool]:
        """Extracts the profiles shown status of the Sketch object.

        Returns:
            bool: The profiles shown status of the Sketch object.
        """
        return getattr(self._obj, 'areProfilesShown', None)

    @property
    @helper_extraction_error
    def origin(self) -> Optional[List[float]]:
        """Extracts the origin of the Sketch object.

        Returns:
            List[float]: The origin of the Sketch object.
        """
        origin = nested_getattr(self._obj, 'origin', None)
        if origin:
            return [
                origin.x,  # 'x'
                origin.y,  # 'y'
                origin.z,  # 'z'
            ]
        return None

    @property
    @helper_extraction_error
    def x_direction(self) -> Optional[List[float]]:
        """Extracts the X direction of the Sketch object.

        Returns:
            List[float]: The X direction of the Sketch object.
        """
        x_direction = nested_getattr(self._obj, 'xDirection', None)
        if x_direction:
            return [
                x_direction.x,  # 'x'
                x_direction.y,  # 'y'
                x_direction.z,  # 'z'
            ]
        return None

    @property
    @helper_extraction_error
    def y_direction(self) -> Optional[List[float]]:
        """Extracts the Y direction of the Sketch object.

        Returns:
            List[float]: The Y direction of the Sketch object.
        """
        y_direction = nested_getattr(self._obj, 'yDirection', None)
        if y_direction:
            return [
                y_direction.x,  # 'x'
                y_direction.y,  # 'y'
                y_direction.z,  # 'z'
            ]
        return None

    @property
    @helper_extraction_error
    def bounding_box(self) -> Optional[Dict[str, float]]:
        """Extracts the bounding box of the Sketch object.

        Returns:
            Dict[str, float]: The bounding box of the Sketch object.
        """
        bbox = getattr(self._obj, 'boundingBox', None)
        if bbox:
            return {
                'bbMinPoint':
                    [bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z],
                'bbMaxPoint':
                    [bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z]
            }
        return None

    @property
    @helper_extraction_error
    def origin_point(self) -> Optional[str]:
        """Extracts the origin point of the Sketch object.

        Returns:
            str: The origin point of the Sketch object.
        """
        return nested_getattr(self._obj, 'originPoint.entityToken', None)

    @property
    @helper_extraction_error
    def is_fully_constrained(self) -> Optional[bool]:
        """Extracts the fully constrained status of the Sketch object.

        Returns:
            bool: The fully constrained status of the Sketch object.
        """
        return getattr(self._obj, 'isFullyConstrained', None)

    @property
    @helper_extraction_error
    def base_or_form_feature(self) -> Optional[str]:
        """Extracts the base or form feature of the Sketch object.

        Returns:
            str: The base or form feature of the Sketch object.
        """
        return nested_getattr(self._obj, 'baseOrFormFeature.entityToken', None)

    @property
    @helper_extraction_error
    def health_state(self) -> Optional[str]:
        """Extracts the health state of the Sketch object.

        Returns:
            str: The health state of the Sketch object.
        """
        return nested_getattr(self._obj, 'healthState', None)

    @property
    @helper_extraction_error
    def error_or_warning_message(self) -> Optional[str]:
        """Extracts the error or warning message of the Sketch object.

        Returns:
            str: The error or warning message of the Sketch object.
        """
        return getattr(self._obj, 'errorOrWarningMessage', None)

    @property
    @helper_extraction_error
    def parent_component(self) -> Optional[str]:
        """
        Returns the parent component.
        """
        return nested_getattr(self._obj, 'parentComponent.entityToken', None)

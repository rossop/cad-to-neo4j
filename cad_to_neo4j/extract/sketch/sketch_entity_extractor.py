"""
Sketch Entity Extractor Module

This module provides a base extractor class for extracting information from
sketch entitys such as SketchPoints, SketchCurves, and SketchDimensions.

Classes:
    - SketchEntityExtractor: Parent class for other sketch entities.
"""

from typing import Optional, List, Dict, Any

import adsk.fusion

from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error


__all__ = ['SketchEntityExtractor']


class SketchEntityExtractor(BaseExtractor):
    """Parent Class for other Sketch Entities"""

    def __init__(self, obj: adsk.fusion.SketchEntity):
        """Initialize the extractor with the Sketch Entities."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the Sketch entity.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_entity_info = {
            'sketchDimensions': self.sketch_dimensions,
            'geometricConstraints': self.geometric_constraints,
            'is2D': self.is2D,
            'isReference': self.is_reference,
            'isFixed': self.is_fixed,
            'isVisible': self.is_visible,
            'referencedEntity': self.referenced_entity,
            'isDeletable': self.is_deletable,
            'isFullyConstrained': self.is_fully_constrained,
            'isLinked': self.is_linked,
            'parentSketch': self.parent_sketch,
        }
        return {**basic_info, **sketch_entity_info}

    @property
    @helper_extraction_error
    def sketch_dimensions(self) -> Optional[List[adsk.fusion.SketchDimension]]:
        """Extracts the Dimensions linked to this Sketch object.

        Returns:
            Optional[List[SketchDimension]]: List of Sketch dimensions that
            are attached to this object.
        """
        sketchDimensions = getattr(self._obj, 'sketchDimensions', [])
        return [getattr(dim, 'entityToken', None) for dim in sketchDimensions]

    @property
    @helper_extraction_error
    def geometric_constraints(self) -> Optional[List[str]]:
        """Extracts the geometric constraints linked to this Sketch object.

        Returns:
            Optional[List[str]]: List of entity tokens for geometric
            constraints that are attached to this object.
        """
        geometric_constraints = getattr(
            self._obj, 'geometricConstraints', [])
        return [nested_getattr(gc, 'entityToken', None)
                for gc in geometric_constraints]

    @property
    @helper_extraction_error
    def is2D(self) -> Optional[bool]:
        """Indicates if this curve lies entirely on the sketch x-y plane.

        Returns:
            Optional[bool]: True if the curve lies entirely on the sketch x-y
                plane, False otherwise.
        """
        return getattr(self._obj, 'is2D', None)

    @property
    @helper_extraction_error
    def is_reference(self) -> Optional[bool]:
        """Indicates if this geometry is a reference.

        Returns:
            Optional[bool]: True if the geometry is a reference,
                False otherwise.
        """
        return getattr(self._obj, 'isReference', None)

    @property
    @helper_extraction_error
    def is_fixed(self) -> Optional[bool]:
        """Indicates if this geometry is "fixed".

        Returns:
            Optional[bool]: True if the geometry is fixed, False otherwise.
        """
        return getattr(self._obj, 'isFixed', None)

    @property
    @helper_extraction_error
    def is_visible(self) -> Optional[bool]:
        """Indicates if this geometry is visible.

        Returns:
            Optional[bool]: True if the geometry is visible, False otherwise.
        """
        return getattr(self._obj, 'isVisible', None)

    @property
    @helper_extraction_error
    def referenced_entity(self) -> Optional[str]:
        """Returns the referenced entity in the case where IsReference is true.

        Returns:
            Optional[str]: Entity token of the referenced entity, or None if
                not applicable.
        """
        if self.is_reference:
            return nested_getattr(
                self._obj, 'referencedEntity.entityToken', None)
        return None

    @property
    @helper_extraction_error
    def is_deletable(self) -> Optional[bool]:
        """Indicates if this sketch entity can be deleted.

        Returns:
            Optional[bool]: True if the sketch entity can be deleted,
                False otherwise.
        """
        return getattr(self._obj, 'isDeletable', None)

    @property
    @helper_extraction_error
    def is_fully_constrained(self) -> Optional[bool]:
        """Indicates if this sketch entity is fully constrained.

        Returns:
            Optional[bool]: True if the sketch entity is fully constrained,
                False otherwise.
        """
        return getattr(self._obj, 'isFullyConstrained', None)

    @property
    @helper_extraction_error
    def is_linked(self) -> Optional[bool]:
        """Indicates if this sketch entity was created by a projection,
        inclusion, or driven by an API script.

        Returns:
            Optional[bool]: True if the entity is linked, False otherwise.
        """
        return getattr(self._obj, 'isLinked', None)

    @property
    @helper_extraction_error
    def parent_sketch(self) -> Optional[str]:
        """
        Returns the parent sketch.
        """
        return nested_getattr(self._obj, 'parentSketch.entityToken', None)

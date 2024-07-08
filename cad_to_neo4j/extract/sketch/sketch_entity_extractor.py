"""
Sketch Entity Extractor Module

This module provides a base extractor class for extracting information from sketch entitys
such as SketchPoints, SketchCurves, and SketchDimensions.

Classes:
    - SketchEntityExtractor: Parent class for other sketch entities.
"""

from typing import Optional, List, Dict, Any
from adsk.fusion import SketchEntity, SketchDimension
from ..base_extractor import BaseExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['SketchEntityExtractor']

class SketchEntityExtractor(BaseExtractor):
    """Parent Class for other Sketch Entities"""

    def __init__(self, obj: SketchEntity):
        """Initialize the extractor with the Sketch Entities."""
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """Extract all information from the Sketch entity.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        basic_info = super().extract_info()
        sketch_entity_info = {
            'sketchDimensions': self.sketchDimensions,
            'geometricConstraints': self.geometricConstraints,
            'is2D': self.is2D,
            'isReference': self.isReference,
            'isFixed': self.isFixed,
            'isVisible': self.isVisible,
            'referencedEntity': self.referencedEntity,
            'isDeletable': self.isDeletable,
            'isFullyConstrained': self.isFullyConstrained,
            'isLinked': self.isLinked,
            'parentSketch': self.parentSketch,
        }
        return {**basic_info, **sketch_entity_info}
    
    @property
    def sketchDimensions(self) -> Optional[List[SketchDimension]]:
        """Extracts the Dimensions linked to this Sketch object.
        
        Returns:
            Optional[List[SketchDimension]]: List of Sketch dimensions that are attached to this object.
        """
        try:
            sketchDimensions = getattr(self._obj, 'sketchDimensions', [])
            return [getattr(dim,'entityToken',None) for dim in sketchDimensions]
        except AttributeError:
            return None
    
    @property
    def geometricConstraints(self) -> Optional[List[str]]:
        """Extracts the geometric constraints linked to this Sketch object.
        
        Returns:
            Optional[List[str]]: List of entity tokens for geometric constraints that are attached to this object.
        """
        try:
            geometric_constraints = getattr(self._obj, 'geometricConstraints', [])
            return [nested_getattr(gc, 'entityToken', None) for gc in geometric_constraints]
        except AttributeError:
            return None

    @property
    def is2D(self) -> Optional[bool]:
        """Indicates if this curve lies entirely on the sketch x-y plane.
        
        Returns:
            Optional[bool]: True if the curve lies entirely on the sketch x-y plane, False otherwise.
        """
        try:
            return getattr(self._obj, 'is2D', None)
        except AttributeError:
            return None

    @property
    def isReference(self) -> Optional[bool]:
        """Indicates if this geometry is a reference.
        
        Returns:
            Optional[bool]: True if the geometry is a reference, False otherwise.
        """
        try:
            return getattr(self._obj, 'isReference', None)
        except AttributeError:
            return None

    @property
    def isFixed(self) -> Optional[bool]:
        """Indicates if this geometry is "fixed".
        
        Returns:
            Optional[bool]: True if the geometry is fixed, False otherwise.
        """
        try:
            return getattr(self._obj, 'isFixed', None)
        except AttributeError:
            return None

    @property
    def isVisible(self) -> Optional[bool]:
        """Indicates if this geometry is visible.
        
        Returns:
            Optional[bool]: True if the geometry is visible, False otherwise.
        """
        try:
            return getattr(self._obj, 'isVisible', None)
        except AttributeError:
            return None
        
    @property
    def referencedEntity(self) -> Optional[str]:
        """Returns the referenced entity in the case where IsReference is true.
        
        Returns:
            Optional[str]: Entity token of the referenced entity, or None if not applicable.
        """
        try:
            if self.isReference:
                return nested_getattr(self._obj, 'referencedEntity.entityToken', None)
            return None
        except AttributeError:
            return None
        
    @property
    def isDeletable(self) -> Optional[bool]:
        """Indicates if this sketch entity can be deleted.
        
        Returns:
            Optional[bool]: True if the sketch entity can be deleted, False otherwise.
        """
        try:
            return getattr(self._obj, 'isDeletable', None)
        except AttributeError:
            return None

    @property
    def isFullyConstrained(self) -> Optional[bool]:
        """Indicates if this sketch entity is fully constrained.
        
        Returns:
            Optional[bool]: True if the sketch entity is fully constrained, False otherwise.
        """
        try:
            return getattr(self._obj, 'isFullyConstrained', None)
        except AttributeError:
            return None
        
    @property
    def isLinked(self) -> Optional[bool]:
        """Indicates if this sketch entity was created by a projection, inclusion, or driven by an API script.
        
        Returns:
            Optional[bool]: True if the entity is linked, False otherwise.
        """
        try:
            return getattr(self._obj, 'isLinked', None)
        except AttributeError:
            return None
        
    @property
    def parentSketch(self) -> Optional[str]:
        """
        Returns the parent sketch.
        """
        try:
            return nested_getattr(self._obj, 'parentSketch.entityToken', None)
        except AttributeError:
            return None
"""
BRep Element Extractor Module

This module provides an extractor base class for extracting information from 
BRep elements such as lumps, shells, faces, edges and vertices.

Classes:
    - BRepElementExtractor: Base extractor for BRep elements.
"""
from typing import Optional, Dict, List, Any
import adsk.core
import adsk.fusion # TODO standardise this import for 
from ..base_extractor import BaseExtractor
from ...utils.general_utils import nested_getattr


__all__ = ['BRepEntityExtractor']

class BRepEntityExtractor(BaseExtractor):
    """
    Base extractor for BRep elements.
    
    This class provides common methods to extract various properties from BRep elements.
    
    Attributes:
        element (adsk.fusion.BRepElement): The BRep element object to extract data from.
    """

    def __init__(self, obj: adsk.fusion.Base):
        """Initializes the BRepElementExtractor with a BRep element object.

        Args:
            obj: The BRep element object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self):
        """Extracts shared infromation across BRepEntities.

        Returns:
            dict: A dictionary containing the exctracted information.
        """
        base_info = super().extract_info()
        brep_entity_info = {
            'body': self.body,
            'area': self.area,
            'volume': self.volume,
            'meshManager': self.meshManager,
            'assemblyContext': self.assemblyContext,
            'nativeObject': self.nativeObject,
        }

        bounding_box_info = self.boundingBox
        if bounding_box_info is not None:
            brep_entity_info.update(bounding_box_info)

        return {**base_info, **brep_entity_info}
        

    @property
    def body(self) -> Optional[str]:
        """
        Returns the parent body of the element.

        Returns:
            Optional[str]: Entity token of the parent body.
        """
        try:
            body = getattr(self._obj, 'body', None)
            return getattr(body, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting body: {e}")
            return None

    @property
    def boundingBox(self) -> Optional[Dict[str, List[float]]]:
        """
        Returns the bounding box of this element.

        Returns:
            Optional[Dict[str, List[float]]]: Dictionary with min and max points of the bounding box.
        """
        try:
            bbox = getattr(self._obj, 'boundingBox', None)
            if bbox:
                return {
                    'min_point': [bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z],
                    'max_point': [bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error extracting bounding box: {e}")
            return None

    @property
    def area(self) -> Optional[float]:
        """
        Returns the area in cm^2.

        Returns:
            Optional[float]: Area of the element.
        """
        try:
            return getattr(self._obj, 'area', None)
        except Exception as e:
            self.logger.error(f"Error extracting area: {e}")
            return None

    @property
    def volume(self) -> Optional[float]:
        """
        Returns the volume in cm^3. Returns 0 if the element is not solid.

        Returns:
            Optional[float]: Volume of the element.
        """
        try:
            return getattr(self._obj, 'volume', None)
        except Exception as e:
            self.logger.error(f"Error extracting volume: {e}")
            return None

    @property
    def meshManager(self) -> Optional[str]:
        """
        Returns the mesh manager object for this element.

        Returns:
            Optional[str]: Entity token of the mesh manager.
        """
        try:
            mesh_manager = getattr(self._obj, 'meshManager', None)
            return getattr(mesh_manager, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting meshManager: {e}")
            return None

    @property
    def assemblyContext(self) -> Optional[str]:
        """
        Returns the assembly occurrence (i.e. the occurrence) of this object in an assembly.

        Returns:
            Optional[str]: Entity token of the assembly context.
        """
        try:
            assemblyContext = getattr(self._obj, 'assemblyContext', None)
            return getattr(assemblyContext, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting assemblyContext: {e}")
            return None

    @property
    def nativeObject(self) -> Optional[str]:
        """
        The NativeObject is the object outside the context of an assembly.

        Returns:
            Optional[str]: Entity token of the native object.
        """
        try:
            nativeObject = getattr(self._obj, 'nativeObject', None)
            return getattr(nativeObject, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting nativeObject: {e}")
            return None
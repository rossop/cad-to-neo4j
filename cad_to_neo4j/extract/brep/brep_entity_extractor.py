"""
BRep Element Extractor Module

This module provides an extractor base class for extracting information from
BRep elements such as lumps, shells, faces, edges and vertices.

Classes:
    - BRepElementExtractor: Base extractor for BRep elements.
"""
from typing import Optional, Dict, List, Any

import adsk.core
import adsk.fusion

from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error


__all__ = ['BRepEntityExtractor']


class BRepEntityExtractor(BaseExtractor):
    """
    Base extractor for BRep elements.

    This class provides common methods to extract various properties from BRep
    elements.

    Attributes:
        element (adsk.fusion.BRepElement): The BRep element object to extract
        data from.
    """

    def __init__(self,
                 obj: adsk.fusion.Base,
                 design_environment_data: Dict[str, Any]):
        """Initializes the BRepElementExtractor with a BRep element object.

        Args:
            obj: The BRep element object to extract information from.
            design (adsk.fusion.Design): The Fusion 360 design object.
        """
        super().__init__(obj)
        self._design_environment_data = design_environment_data

    def extract_info(self) -> Dict[str, Any]:
        """Extracts shared infromation across BRepEntities.

        Returns:
            dict: A dictionary containing the exctracted information.
        """
        base_info = super().extract_info()
        brep_entity_info = {
            'body': self.body,
            'area': self.area,
            'volume': self.volume,
            'meshManager': self.mesh_manager,
            'assemblyContext': self.assembly_context,
            'nativeObject': self.native_object,
        }

        bounding_box_info = self.bounding_box
        if bounding_box_info is not None:
            brep_entity_info.update(bounding_box_info)

        if self._design_environment_data is not None:
            brep_entity_info.update(self._design_environment_data)

        return {**base_info, **brep_entity_info}

    @property
    @helper_extraction_error
    def body(self) -> Optional[str]:
        """
        Returns the parent body of the element.

        Returns:
            Optional[str]: Entity token of the parent body.
        """
        return nested_getattr(self._obj, 'body.entityToken', None)

    @property
    @helper_extraction_error
    def bounding_box(self) -> Optional[Dict[str, List[float]]]:
        """
        Returns the bounding box of this element.

        Returns:
            Optional[Dict[str, List[float]]]: Dictionary with min and max p
            oints of the bounding box.
        """
        bbox = getattr(self._obj, 'boundingBox', None)
        if bbox:
            return {
                'min_point': [
                    bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z
                    ],
                'max_point': [
                    bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z
                    ],
            }
        return None

    @property
    @helper_extraction_error
    def area(self) -> Optional[float]:
        """
        Returns the area in cm^2.

        Returns:
            Optional[float]: Area of the element.
        """
        return getattr(self._obj, 'area', None)

    @property
    @helper_extraction_error
    def volume(self) -> Optional[float]:
        """
        Returns the volume in cm^3. Returns 0 if the element is not solid.

        Returns:
            Optional[float]: Volume of the element.
        """
        return getattr(self._obj, 'volume', None)

    @property
    @helper_extraction_error
    def mesh_manager(self) -> Optional[str]:
        """
        Returns the mesh manager object for this element.

        Returns:
            Optional[str]: Entity token of the mesh manager.
        """
        return nested_getattr(self._obj, 'meshManager.entityToken', None)

    @property
    @helper_extraction_error
    def assembly_context(self) -> Optional[str]:
        """
        Returns the assembly occurrence (i.e. the occurrence) of this object
        in an assembly.

        Returns:
            Optional[str]: Entity token of the assembly context.
        """
        return nested_getattr(self._obj, 'assemblyContext.entityToken', None)

    @property
    @helper_extraction_error
    def native_object(self) -> Optional[str]:
        """
        The NativeObject is the object outside the context of an assembly.

        Returns:
            Optional[str]: Entity token of the native object.
        """
        return nested_getattr(self._obj, 'nativeObject.entityToken', None)

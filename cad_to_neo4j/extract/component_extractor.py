"""
Component Extractor Module

This module provides an extractor class for extracting information from Component objects.

Classes:
    - ComponentExtractor: Extractor for Component objects.
"""

from typing import Dict, Optional, List, Union
from adsk.fusion import Component
from .base_extractor import BaseExtractor

__all__ = ['ComponentExtractor']


class ComponentExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Component objects."""

    def __init__(self, obj: Component) -> None:
        """
        Initializes the ComponentExtractor with a Component object.

        Args:
            obj (Component): The Component object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Union[str, float, List[float]]]]:
        """
        Extracts component information, ensuring a flat structure.

        Returns:
            Dict[str, Optional[Union[str, float, List[float]]]]:
            A dictionary containing basic and detailed information of the component.
        """
        basic_info: Dict[str, Optional[Union[str, float]]] = super().extract_info()
        component_info: Dict[str, Optional[Union[str, float, List[float]]]] = {
            'bRepBodies': self.bRepBodies,
            'features': self.features,
            'sketches': self.sektches,
            'volume': self.volume,
            'fusionId': self.id,
            # 'originConstructionPoint': self.originConstructionPoint,
            # 'xConstructionAxis': self.xConstructionAxis,
            # 'xYConstructionPlane': self.xYConstructionPlane,
            # 'xZConstructionPlane': self.xZConstructionPlane,
            # 'yConstructionAxis': self.yConstructionAxis,
            # 'yZConstructionPlane': self.yZConstructionPlane,
            # 'zConstructionAxis': self.zConstructionAxis,
        }

        if self.boundingBox is not None:
            component_info.update(self.boundingBox)

        return {**basic_info, **component_info}
    
    @property
    def id(self) -> str:
        """
        Returns the persistent ID of the component.

        Returns:
            str: The persistent ID of the component.
        """
        return self._obj.id

    @property
    def boundingBox(self) -> Optional[Dict[str, List[float]]]:
        """
        Returns the 3D bounding box of the component.

        Returns:
            Optional[Dict[str, List[float]]]: Dictionary with min and max points 
            of the bounding box.
        """
        try:
            bbox = getattr(self._obj, 'boundingBox', None)
            if bbox:
                return {
                    'bbMinPoint': [bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z],
                    'bbMaxPoint': [bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error extracting bounding box: {e}")
            return None

    @property
    def bRepBodies(self) -> List[str]:
        """
        Returns a list of entity tokens from the BRep bodies of the Component.

        Returns:
            List[str]: A list of entity tokens from the BRep bodies of the Component.
        """
        return list(map(lambda body: body.entityToken, self._obj.bRepBodies))

    @property
    def sektches(self) -> List[str]:
        """
        Returns a list of entity tokens from the Sketches of the Component.

        Returns:
            List[str]: A list of entity tokens from the Sketches of the Component.
        """
        return list(map(lambda sketch: sketch.entityToken, self._obj.sketches))

    @property
    def features(self) -> List[str]:
        """
        Returns a list of entity tokens from the features of the Component.

        Returns:
            List[str]: A list of entity tokens from the features of the Component.
        """
        return list(map(lambda feat: feat.entityToken, self._obj.features))

    @property
    def originConstructionPoint(self) -> Optional[str]:
        """
        Returns the entity token of the origin construction point of the component.

        Returns:
            Optional[str]: The entity token of the origin construction point.
        """
        return self.extract_entity_token(self._obj.originConstructionPoint)

    @property
    def xConstructionAxis(self) -> Optional[str]:
        """
        Returns the entity token of the X origin construction axis of the component.

        Returns:
            Optional[str]: The entity token of the X construction axis.
        """
        return self.extract_entity_token(self._obj.xConstructionAxis)

    @property
    def xYConstructionPlane(self) -> Optional[str]:
        """
        Returns the entity token of the XY construction plane of the component.

        Returns:
            Optional[str]: The entity token of the XY construction plane.
        """
        return self.extract_entity_token(self._obj.xYConstructionPlane)

    @property
    def xZConstructionPlane(self) -> Optional[str]:
        """
        Returns the entity token of the XZ construction plane of the component.

        Returns:
            Optional[str]: The entity token of the XZ construction plane.
        """
        return self.extract_entity_token(self._obj.xZConstructionPlane)

    @property
    def yConstructionAxis(self) -> Optional[str]:
        """
        Returns the entity token of the Y origin construction axis of the component.

        Returns:
            Optional[str]: The entity token of the Y construction axis.
        """
        return self.extract_entity_token(self._obj.yConstructionAxis)

    @property
    def yZConstructionPlane(self) -> Optional[str]:
        """
        Returns the entity token of the YZ construction plane of the component.

        Returns:
            Optional[str]: The entity token of the YZ construction plane.
        """
        return self.extract_entity_token(self._obj.yZConstructionPlane)

    @property
    def zConstructionAxis(self) -> Optional[str]:
        """
        Returns the entity token of the Z origin construction axis of the component.

        Returns:
            Optional[str]: The entity token of the Z construction axis.
        """
        return self.extract_entity_token(self._obj.zConstructionAxis)

    @property
    def volume(self) -> Optional[float]:
        """
        Returns the volume of the component.

        Returns:
            Optional[float]: The volume of the component in cubic centimeters.
        """
        try:
            physical_props = self._obj.getPhysicalProperties()
            return physical_props.volume if physical_props else None
        except Exception as e:
            self.logger.error(f"Error extracting volume: {e}")
            return None

    def extract_entity_token(self, entity: Optional[object]) -> Optional[str]:
        """
        Helper method to extract the entityToken of a given entity.

        Args:
            entity (Optional[object]): The entity from which to extract the token.

        Returns:
            Optional[str]: The entityToken of the entity, or None if not available.
        """
        return getattr(entity, 'entityToken', None)

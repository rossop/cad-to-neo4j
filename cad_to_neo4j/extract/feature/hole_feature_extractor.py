"""
Hole Feature Extractor Module

This module provides an extractor class for extracting information from HoleFeature objects.

Classes:
    - HoleFeatureExtractor: Extractor for HoleFeature objects.
"""
from typing import Optional, Any, Dict, List
from adsk.fusion import (
        HoleFeature,
        AtCenterHolePositionDefinition, 
        OnEdgeHolePositionDefinition, 
        PlaneAndOffsetsHolePositionDefinition, 
        PointHolePositionDefinition, 
        SketchPointHolePositionDefinition, 
        SketchPointsHolePositionDefinition
    )
import traceback
from .feature_extractor import FeatureExtractor
from ...utils.general_utils import nested_getattr

__all__ = ['HoleFeatureExtractor']

class HoleFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from HoleFeature objects."""

    def __init__(self, obj: HoleFeature):
        """Initialize the extractor with the HoleFeature obj."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the HoleFeature obj.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        hole_info = {
            'position': self.position,
            'direction': self.direction,
            'holeType': self.holeType,
            'holeDiameter': self.holeDiameter,
            'tip_angle': self.tip_angle,
            'counterboreDiameter': self.counterboreDiameter,
            'counterboreDepth': self.counterboreDepth,
            'countersinkDiameter': self.countersinkDiameter,
            'countersinkAngle': self.countersinkAngle,
            'isDefaultDirection': self.isDefaultDirection,
        }
        # Add hole position information if available
        # hole_position_info = self.holePositionDefinition # TODO define
        # if hole_position_info is not None:
        #     hole_info.update(hole_position_info)

        # Add extent information if available
        extent_info = self.extentDefinition #TODO add all 6 HolePositionDefinition
        if extent_info is not None:
            hole_info.update(extent_info)

        return {**feature_info, **hole_info}

    @property
    def position(self) -> Optional[List[float]]:
        """Returns the position of the hole as a vector."""
        try:
            point = getattr(self._obj,'position', None)
            if point is not None:
                return [getattr(point, 'x', None),
                        getattr(point, 'y', None),
                        getattr(point, 'z', None)]
            else:
                return None
            
        except AttributeError as e:
            self.logger.error(f'Error extracting position: {e}\n{traceback.format_exc()}')
            return None

    @property
    def direction(self) -> Optional[List[float]]:
        """Returns the direction of the hole as a vector."""
        try:
            vector = getattr(self._obj,'direction', None)
            if vector is not None:    
                return [getattr(vector, 'x', None),
                        getattr(vector, 'y', None),
                        getattr(vector, 'z', None)]
            else:
                return None
            
        except AttributeError as e:
            self.logger.error(f'Error extracting direction: {e}\n{traceback.format_exc()}')
            return None

    @property
    def holeType(self) -> Optional[str]:
        """
        Returns the current type of hole this feature represents.
        
        SimpleHoleType = 0
        CounterboreHoleType = 1
        CountersinkHoleType = 2
        """
        try:
            holeTypes_map = {
                0: 'SimpleHoleType',
                1: 'CounterboreHoleType',
                2: 'CountersinkHoleType',
            }
            holeType = nested_getattr(self._obj, 'holeType', None)
            if holeType is not None:
                return holeTypes_map[holeType]
            else:
                return None
        except AttributeError as e:
            self.logger.error(f'Error extracting hole type: {e}\n{traceback.format_exc()}')
            return None

    @property
    def holeDiameter(self) -> Optional[float]:
        """Returns the model parameter controlling the hole diameter."""
        try:
            return nested_getattr(self._obj, 'holeDiameter.value', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting hole diameter: {e}\n{traceback.format_exc()}')
            return None

    @property
    def tip_angle(self) -> Optional[float]:
        """Returns the model parameter controlling the angle of the tip of the hole."""
        try:
            return nested_getattr(self._obj, 'tipAngle.value', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting tip angle: {e}\n{traceback.format_exc()}')
            return None

    @property
    def counterboreDiameter(self) -> Optional[float]:
        """Returns the model parameter controlling the counterbore diameter."""
        try:
            return nested_getattr(self._obj, 'counterboreDiameter.value', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting counterbore diameter: {e}\n{traceback.format_exc()}')
            return None

    @property
    def counterboreDepth(self) -> Optional[float]:
        """Returns the model parameter controlling the counterbore depth."""
        try:
            return nested_getattr(self._obj, 'counterboreDepth.value', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting counterbore depth: {e}\n{traceback.format_exc()}')
            return None

    @property
    def countersinkDiameter(self) -> Optional[float]:
        """Returns the model parameter controlling the countersink diameter."""
        try:
            return nested_getattr(self._obj, 'countersinkDiameter.value', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting countersink diameter: {e}\n{traceback.format_exc()}')
            return None

    @property
    def countersinkAngle(self) -> Optional[float]:
        """Returns the model parameter controlling the countersink angle."""
        try:
            return nested_getattr(self._obj, 'countersinkAngle.value', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting countersink angle: {e}\n{traceback.format_exc()}')
            return None

    @property
    def isDefaultDirection(self) -> Optional[bool]:
        """Gets if the hole is in the default direction or not."""
        try:
            return nested_getattr(self._obj, 'isDefaultDirection', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting isDefaultDirection: {e}\n{traceback.format_exc()}')
            return None

    @property
    def extentDefinition(self) -> Optional[str]:
        """Gets the definition object that is defining the extent of the hole."""
        try:
            extentDefinition = nested_getattr(self._obj, 'extentDefinition', None)
            return self.extract_extent_info(extentDefinition, 'extentDefinition')
        except AttributeError as e:
            self.logger.error(f'Error extracting extent definition: {e}\n{traceback.format_exc()}')
            return None

    @property
    def holePositionDefinition(self) -> Optional[str]:
        """Returns a HolePositionDefinition object that provides access to the information used to define the position of the hole."""
        try:
            return nested_getattr(self._obj, 'holePositionDefinition', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting hole position definition: {e}\n{traceback.format_exc()}')
            return None

    @property
    def nativeObject(self) -> Optional[str]:
        """The NativeObject is the object outside the context of an assembly and in the context of its parent component."""
        try:
            return nested_getattr(self._obj, 'nativeObject', None)
        except AttributeError as e:
            self.logger.error(f'Error extracting native object: {e}\n{traceback.format_exc()}')
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
            if extent_root is None:
                return None

            extent_info = {
                f'{prefix}Type': type(extent_root).__name__,
                f'{prefix}Taper_angle': nested_getattr(extent_root, 'taperAngle.value', None), #TODO review if you should remove
                f'{prefix}IsPositiveDirection': nested_getattr(extent_root, 'isPositiveDirection', None), #TODO review if you should remove
            }

            def extract_at_center(extent_root):
                return {
                    f'{prefix}Plane': nested_getattr(extent_root, 'planarEntity.entityToken', None),
                    f'{prefix}CenterEdge': nested_getattr(extent_root, 'centerEdge.entityToken', None),
                }

            def extract_on_edge(extent_root):
                return {
                    f'{prefix}Plane': nested_getattr(extent_root, 'planarEntity.entityToken', None),
                    f'{prefix}Edge': nested_getattr(extent_root, 'edge.entityToken', None),
                    f'{prefix}Position': nested_getattr(extent_root, 'position.name', None),
                }

            def extract_plane_and_offsets(extent_root):
                return {
                    f'{prefix}Plane': nested_getattr(extent_root, 'planarEntity.entityToken', None),
                    f'{prefix}Edge_one': nested_getattr(extent_root, 'edgeOne.entityToken', None),
                    f'{prefix}OffsetOne': nested_getattr(extent_root, 'offsetOne.value', None),
                    f'{prefix}Edge_two': nested_getattr(extent_root, 'edgeTwo.entityToken', None),
                    f'{prefix}OffsetTwo': nested_getattr(extent_root, 'offsetTwo.value', None),
                }

            def extract_point(extent_root):
                return {
                    f'{prefix}Plane': nested_getattr(extent_root, 'planarEntity.entityToken', None),
                    f'{prefix}_point': nested_getattr(extent_root, 'point.entityToken', None),
                }

            def extract_sketch_point(extent_root):
                return {
                    f'{prefix}SketchPoint': nested_getattr(extent_root, 'sketchPoint.entityToken', None),
                }

            def extract_sketch_points(extent_root):
                return {
                    f'{prefix}SketchPoints': [nested_getattr(point, 'entityToken', None) for point in nested_getattr(extent_root, 'sketchPoints', [])],
                }

            extractors = {
                AtCenterHolePositionDefinition: extract_at_center,
                OnEdgeHolePositionDefinition: extract_on_edge,
                PlaneAndOffsetsHolePositionDefinition: extract_plane_and_offsets,
                PointHolePositionDefinition: extract_point,
                SketchPointHolePositionDefinition: extract_sketch_point,
                SketchPointsHolePositionDefinition: extract_sketch_points,
            }

            extent_info.update(extractors.get(type(extent_root), lambda x: {})(extent_root))

            return extent_info

        except AttributeError as e:
            self.logger.error(f'Error extracting extent info: {e}\n{traceback.format_exc()}')
            return None

"""
Hole Feature Extractor Module

This module provides an extractor class for extracting information from
HoleFeature objects.

Classes:
    - HoleFeatureExtractor: Extractor for HoleFeature objects.
"""
from typing import Optional, Any, Dict, List

import adsk.fusion
import adsk.core

from .feature_extractor import FeatureExtractor
from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error


__all__ = ['HoleFeatureExtractor']


class HoleFeatureExtractor(FeatureExtractor):
    """
    Extractor for extracting detailed information from HoleFeature objects.
    """

    def __init__(self, obj: adsk.fusion.HoleFeature):
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
            'holeType': self.hole_type,
            'holeDiameterValue': self.hole_diameter_value,
            'holeDiameterToken': self.hole_diameter_token,
            'tipAngleValue': self.tip_angle_value,
            'tipAngleToken': self.tip_angle_token,
            'counterboreDiameterValue': self.counterbore_diameter_value,
            'counterboreDiameterToken': self.counterbore_diameter_token,
            'counterboreDepthValue': self.counterbore_depth_value,
            'counterboreDepthToken': self.counterbore_depth_token,
            'countersinkDiameterValue': self.countersink_diameter_value,
            'countersinkDiameterToken': self.countersink_diameter_token,
            'countersink_angleValue': self.countersink_angle_value,
            'countersink_angleToken': self.countersink_angle_token,
            'isDefaultDirection': self.is_default_direction,
            # 'holePositionDefinition': self.hole_position_definition,
            'nativeObject': self.native_object,
        }

        # Add extent information if available
        extent_info = self.extent_definition
        if extent_info is not None:
            hole_info.update(extent_info)

        return {**feature_info, **hole_info}

    @property
    @helper_extraction_error
    def position(self) -> Optional[List[float]]:
        """Returns the position of the hole as a vector."""
        point = getattr(self._obj, 'position', None)
        if point is not None:
            return [getattr(point, 'x', None),
                    getattr(point, 'y', None),
                    getattr(point, 'z', None)]
        else:
            return None

    @property
    @helper_extraction_error
    def direction(self) -> Optional[List[float]]:
        """Returns the direction of the hole as a vector."""
        vector = getattr(self._obj, 'direction', None)
        if vector is not None:
            return [getattr(vector, 'x', None),
                    getattr(vector, 'y', None),
                    getattr(vector, 'z', None)]
        else:
            return None

    @property
    @helper_extraction_error
    def hole_type(self) -> Optional[str]:
        """
        Returns the current type of hole this feature represents.

        SimpleHoleType = 0
        CounterboreHoleType = 1
        CountersinkHoleType = 2
        """
        hole_types_map = {
            0: 'SimpleHoleType',
            1: 'CounterboreHoleType',
            2: 'CountersinkHoleType',
        }
        hole_type = nested_getattr(self._obj, 'holeType', None)
        if hole_type is not None:
            return hole_types_map[hole_type]
        else:
            return None

    @property
    @helper_extraction_error
    def hole_diameter_value(self) -> Optional[float]:
        """Returns the value of the hole diameter."""
        return nested_getattr(self._obj, 'holeDiameter.value', None)

    @property
    @helper_extraction_error
    def hole_diameter_token(self) -> Optional[str]:
        """Returns the entityToken of the hole diameter."""
        return nested_getattr(self._obj, 'holeDiameter.entityToken', None)

    @property
    @helper_extraction_error
    def tip_angle_value(self) -> Optional[float]:
        """Returns the value of the tip angle."""
        return nested_getattr(self._obj, 'tipAngle.value', None)

    @property
    @helper_extraction_error
    def tip_angle_token(self) -> Optional[str]:
        """Returns the entityToken of the tip angle."""
        return nested_getattr(self._obj, 'tipAngle.entityToken', None)

    @property
    @helper_extraction_error
    def counterbore_diameter_value(self) -> Optional[float]:
        """Returns the value of the counterbore diameter."""
        return nested_getattr(self._obj, 'counterboreDiameter.value', None)

    @property
    @helper_extraction_error
    def counterbore_diameter_token(self) -> Optional[str]:
        """Returns the entityToken of the counterbore diameter."""
        return nested_getattr(
            self._obj, 'counterboreDiameter.entityToken', None)

    @property
    @helper_extraction_error
    def counterbore_depth_value(self) -> Optional[float]:
        """Returns the value of the counterbore depth."""
        return nested_getattr(self._obj, 'counterboreDepth.value', None)

    @property
    @helper_extraction_error
    def counterbore_depth_token(self) -> Optional[str]:
        """Returns the entityToken of the counterbore depth."""
        return nested_getattr(self._obj, 'counterboreDepth.entityToken', None)

    @property
    @helper_extraction_error
    def countersink_diameter_value(self) -> Optional[float]:
        """Returns the value of the countersink diameter."""
        return nested_getattr(self._obj, 'countersinkDiameter.value', None)

    @property
    @helper_extraction_error
    def countersink_diameter_token(self) -> Optional[str]:
        """Returns the entityToken of the countersink diameter."""
        return nested_getattr(
            self._obj, 'countersinkDiameter.entityToken', None)

    @property
    @helper_extraction_error
    def countersink_angle_value(self) -> Optional[float]:
        """Returns the value of the countersink angle."""
        return nested_getattr(self._obj, 'countersinkAngle.value', None)

    @property
    @helper_extraction_error
    def countersink_angle_token(self) -> Optional[str]:
        """Returns the entityToken of the countersink angle."""
        return nested_getattr(self._obj, 'countersinkAngle.entityToken', None)

    @property
    @helper_extraction_error
    def is_default_direction(self) -> Optional[bool]:
        """Gets if the hole is in the default direction or not."""
        return nested_getattr(self._obj, 'isDefaultDirection', None)

    @property
    @helper_extraction_error
    def extent_definition(self) -> Optional[Dict[str, Any]]:
        """
        Gets the definition object that is defining the extent of the hole.
        """
        extent_definition = nested_getattr(self._obj, 'extentDefinition', None)
        return self.extract_extent_info(extent_definition, 'extentDefinition')

    @property
    @helper_extraction_error
    def hole_position_definition(self) -> Optional[str]:
        """
        Returns a HolePositionDefinition object that provides access to the
        information used to define the position of the hole.
        """
        return nested_getattr(self._obj, 'holePositionDefinition', None)

    @property
    @helper_extraction_error
    def native_object(self) -> Optional[str]:
        """
        The NativeObject is the object outside the context of an assembly and
        in the context of its parent component.
        """
        return nested_getattr(self._obj, 'nativeObject', None)

    @helper_extraction_error
    def extract_extent_info(self,
                            extent_root: Any,
                            prefix: str) -> Optional[Dict[str, Any]]:
        """Extracts the extent definition information.

        Args:
            extent_root (Any): The extent definition object.
            prefix (str): The prefix to add to the keys in the returned
                dictionary.

        Returns:
            dict: A dictionary containing the extracted extent information.
        """
        if extent_root is None:
            return None

        extent_info = {
            f'{prefix}Type': type(extent_root).__name__,
            f'{prefix}TaperAngleValue': nested_getattr(
                extent_root, 'taperAngle.value', None),
            f'{prefix}TaperAngleToken': nested_getattr(
                extent_root, 'taperAngle.entityToken', None),
            f'{prefix}IsPositiveDirection': nested_getattr(
                extent_root, 'isPositiveDirection', None),
        }

        def extract_at_center(extent_root):
            return {
                f'{prefix}PlaneToken': nested_getattr(
                    extent_root, 'planarEntity.entityToken', None),
                f'{prefix}CenterEdgeToken': nested_getattr(
                    extent_root, 'centerEdge.entityToken', None),
            }

        def extract_on_edge(extent_root):
            return {
                f'{prefix}PlaneToken': nested_getattr(
                    extent_root, 'planarEntity.entityToken', None),
                f'{prefix}EdgeToken': nested_getattr(
                    extent_root, 'edge.entityToken', None),
                f'{prefix}PositionToken': nested_getattr(
                    extent_root, 'position.name', None),
            }

        def extract_plane_and_offsets(extent_root):
            return {
                f'{prefix}PlaneToken': nested_getattr(
                    extent_root, 'planarEntity.entityToken', None),
                f'{prefix}EdgeOneToken': nested_getattr(
                    extent_root, 'edgeOne.entityToken', None),
                f'{prefix}OffsetOneToken': nested_getattr(
                    extent_root, 'offsetOne.value', None),
                f'{prefix}EdgeTwoToken': nested_getattr(
                    extent_root, 'edgeTwo.entityToken', None),
                f'{prefix}OffsetTwoToken': nested_getattr(
                    extent_root, 'offsetTwo.value', None),
            }

        def extract_point(extent_root):
            return {
                f'{prefix}Plane': nested_getattr(
                    extent_root, 'planarEntity.entityToken', None),
                f'{prefix}Point': nested_getattr(
                    extent_root, 'point.entityToken', None),
            }

        def extract_sketch_point(extent_root):
            return {
                f'{prefix}SketchPoint': nested_getattr(
                    extent_root, 'sketchPoint.entityToken', None),
            }

        def extract_sketch_points(extent_root):
            return {
                f'{prefix}SketchPoints': [nested_getattr(
                    point, 'entityToken', None)
                    for point in nested_getattr(
                        extent_root, 'sketchPoints', [])],
            }

        extractors = {
            adsk.fusion.AtCenterHolePositionDefinition:
                extract_at_center,
            adsk.fusion.OnEdgeHolePositionDefinition:
                extract_on_edge,
            adsk.fusion.PlaneAndOffsetsHolePositionDefinition:
                extract_plane_and_offsets,
            adsk.fusion.PointHolePositionDefinition:
                extract_point,
            adsk.fusion.SketchPointHolePositionDefinition:
                extract_sketch_point,
            adsk.fusion.SketchPointsHolePositionDefinition:
                extract_sketch_points,
        }

        extent_info.update(extractors.get(
            type(extent_root), lambda x: {})(extent_root))

        return extent_info

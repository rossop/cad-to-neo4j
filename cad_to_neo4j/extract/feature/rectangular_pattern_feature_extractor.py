"""
Rectangular Pattern Feature Extractor Module

This module provides an extractor class for extracting information from
RectangularPatternFeature objects.

Classes:
    - RectangularPatternFeatureExtractor: Extractor for
        RectangularPatternFeature objects.
"""

from typing import Optional, Dict, List, Any

import adsk.core
import adsk.fusion

from .feature_extractor import FeatureExtractor
from ...utils.extraction_utils import helper_extraction_error

__all__ = ['RectangularPatternFeatureExtractor']


class RectangularPatternFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from
    RectangularPatternFeature objects."""

    def __init__(self, obj: adsk.fusion.RectangularPatternFeature):
        """
        Initialize the extractor with the RectangularPatternFeature element.
        """
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract all information from the RectangularPatternFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        pattern_info: Dict[str, Any] = {
            'inputEntities': self.input_entities,
            'directionOneEntity': self.direction_one_entity,
            'directionTwoEntity': self.direction_two_entity,
            'quantityOne': self.quantity_one,
            'quantityTwo': self.quantity_two,
            'distanceOne': self.distance_one,
            'distanceTwo': self.distance_two,
            'isSymmetricInDirectionOne': self.is_symmetric_in_direction_one,
            'isSymmetricInDirectionTwo': self.is_symmetric_in_direction_two,
            'patternDistanceType': self.pattern_distance_type,
            'suppressedElementsIds': self.suppressed_elements_ids,
            'resultFeatures': self.result_features,
            'faces': self.pattern_faces,
            # 'patternElements': self.pattern_element_faces,
        }

        return {**feature_info, **pattern_info}

    @property
    @helper_extraction_error
    def input_entities(self) -> Optional[List[str]]:
        """Extracts the input entities of the pattern."""
        input_entities = self._obj.inputEntities
        return [entity.entityToken
                for entity in input_entities] if input_entities else []

    @property
    @helper_extraction_error
    def direction_one_entity(self) -> Optional[str]:
        """Extracts the first direction entity."""
        direction_one = self._obj.directionOneEntity
        return direction_one.entityToken if direction_one else None

    @property
    def direction_two_entity(self) -> Optional[str]:
        """Extracts the second direction entity."""
        direction_two = self._obj.directionTwoEntity
        return direction_two.entityToken if direction_two else None

    @property
    def quantity_one(self) -> Optional[float]:
        """Extracts the number of instances in the first direction."""
        return getattr(self._obj.quantityOne, 'value', None)

    @property
    @helper_extraction_error
    def quantity_two(self) -> Optional[float]:
        """Extracts the number of instances in the second direction."""
        return getattr(self._obj.quantityTwo, 'value', None)

    @property
    @helper_extraction_error
    def distance_one(self) -> Optional[float]:
        """Extracts the distance in the first direction."""
        return getattr(self._obj.distanceOne, 'value', None)

    @property
    @helper_extraction_error
    def distance_two(self) -> Optional[float]:
        """Extracts the distance in the second direction."""
        return getattr(self._obj.distanceTwo, 'value', None)

    @property
    @helper_extraction_error
    def is_symmetric_in_direction_one(self) -> Optional[bool]:
        """Extracts whether the pattern is symmetric in the first direction."""
        return self._obj.isSymmetricInDirectionOne

    @property
    @helper_extraction_error
    def is_symmetric_in_direction_two(self) -> Optional[bool]:
        """
        Extracts whether the pattern is symmetric in the second direction.
        """
        return self._obj.isSymmetricInDirectionTwo

    @property
    @helper_extraction_error
    def pattern_distance_type(self) -> Optional[str]:
        """
        Extracts how the distance between elements is computed.
        Defines the different ways to specify the spacing between elements in
        a pattern.
        """
        extent_pattern_distance_type: int = 0
        spacing_pattern_distance_type: int = 1

        direction_value: int = self._obj.patternDistanceType
        if direction_value == extent_pattern_distance_type:
            return 'Extent'
        elif direction_value == spacing_pattern_distance_type:
            return 'Spacing'
        else:
            return 'Unknown'

    @property
    @helper_extraction_error
    def suppressed_elements_ids(self) -> Optional[List[int]]:
        """Extracts the IDs of suppressed elements."""
        return self._obj.suppressedElementsIds

    @property
    @helper_extraction_error
    def pattern_faces(self) -> Optional[List[str]]:
        """
        Extracts the faces from the rectangular pattern feature's bodies.
        """
        # Get the bodies associated with the pattern feature
        faces = self._obj.faces
        if not faces:
            return []

        return list(map(lambda face: face.entityToken, faces))

    @property
    @helper_extraction_error
    def pattern_element_faces(self) -> Optional[List[str]]:
        """
        Extracts the pattern elements faces and encodes them into a single
        string format. Each string contains the occurrence name, and face
        entityToken, separated by '::'.

        Returns:
            list: A list of strings representing pattern elements with encoded
            data.

        ISSUE: despite faces being accessible from CLI they aren't via API
        """
        elements = self._obj.patternElements

        if elements:
            element_data = []
            for pattern_element in elements:
                # Call the helper function to retrieve the encoded face
                # strings
                faces_data = \
                    self._get_pattern_element_faces(pattern_element)
                if faces_data:
                    element_data.extend(faces_data)

            return element_data
        return []

    @helper_extraction_error
    def _get_pattern_element_faces(
            self,
            pattern_element) -> Optional[List[str]]:
        """
        Private helper function to retrieve and encode faces from a pattern
        element.

        Args:
            pattern_element (PatternElement): The pattern element object to
            extract faces from.

        Returns:
            Optional[List[str]]: A list of strings representing the pattern
            element and associated faces, or None if faces are not retrievable.
        """
        element_faces_data = []

        if pattern_element.isValid:
            # Attempt to access the faces
            if hasattr(pattern_element, 'faces'):
                try:
                    faces = pattern_element.faces
                    if faces:
                        for face in faces:
                            combined_str = \
                                f"""{pattern_element.name}::
                                {face.entityToken}"""
                            element_faces_data.append(combined_str)
                    else:
                        debug_msg: str = (
                            f"Pattern element {pattern_element.id}"
                            "has no faces."
                            )
                        self.logger.debug(debug_msg)
                except RuntimeError as re:
                    self._log_extraction_error(
                        "faces for pattern element "
                        f"{pattern_element.id}", re
                        )
                except Exception as e:
                    self._log_extraction_error(
                        "faces for pattern element "
                        f"{pattern_element.id}", e
                        )
            else:
                debug_msg: str = (
                    f"Pattern element {pattern_element.id} "
                    "does not have a 'faces' attribute."
                )
                self.logger.debug(debug_msg)
        else:
            msg: str = f"Pattern element {pattern_element.id} is invalid."
            self.logger.warning(msg)

        return element_faces_data if element_faces_data else None

    @property
    @helper_extraction_error
    def result_features(self) -> Optional[List[str]]:
        """Extracts the features created for this pattern."""
        features = self._obj.resultFeatures
        return [feature.entityToken
                for feature in features] if features else []

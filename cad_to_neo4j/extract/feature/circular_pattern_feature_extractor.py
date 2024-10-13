"""
Circular Pattern Feature Extractor Module

This module provides an extractor class for extracting information from
CircularPatternFeature objects.

Classes:
    - CircularPatternFeatureExtractor: Extractor for CircularPatternFeature
        objects.
"""

from typing import Optional, Dict, Any, List

import adsk.fusion
import adsk.core

from .feature_extractor import FeatureExtractor
from ..base_extractor import BaseExtractor

__all__ = ['CircularPatternFeatureExtractor']


class CircularPatternFeatureExtractor(FeatureExtractor):
    """
    Extractor for extracting detailed information from CircularPatternFeature
    objects.
    """

    def __init__(self, obj: adsk.fusion.CircularPatternFeature) -> None:
        """
        Initialize the extractor with the CircularPatternFeature object.

        Args:
            obj (adsk.fusion.CircularPatternFeature): The
                CircularPatternFeature object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the CircularPatternFeature element.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted information.
        """
        feature_info: Dict[str, Any] = super().extract_info()
        circular_pattern_info: Dict[str, Any] = {
            'inputEntities': self.input_entities,
            'axis': self.axis,
            'quantity': self.quantity,
            'totalAngle': self.total_angle,
            'isSymmetric': self.is_symmetric,
            'patternComputeOption': self.pattern_compute_option,
            'suppressedElementsIds': self.suppressed_elements_ids,
        }

        return {**feature_info, **circular_pattern_info}

    @property
    @BaseExtractor.safe_extraction
    def input_entities(self) -> Optional[List[str]]:
        """
        Extracts the input entities used in the circular pattern feature.

        Returns:
            Optional[List[str]]: A list of entity tokens for input entities.
        """
        entities: adsk.core.ObjectCollection = self._obj.inputEntities
        return [entity.entityToken for entity in entities]

    @property
    @BaseExtractor.safe_extraction
    def axis(self) -> Optional[str]:
        """
        Extracts the entity token for the axis used in the circular pattern.

        Returns:
            Optional[str]: The entity token for the axis.
        """
        return self._obj.axis.entityToken

    @property
    @BaseExtractor.safe_extraction
    def quantity(self) -> Optional[float]:
        """
        Extracts the quantity of elements in the circular pattern.

        Returns:
            Optional[float]: The quantity value.
        """
        return self._obj.quantity.value

    @property
    @BaseExtractor.safe_extraction
    def total_angle(self) -> Optional[float]:
        """
        Extracts the total angle of the circular pattern.

        Returns:
            Optional[float]: The total angle value.
        """
        return self._obj.totalAngle.value

    @property
    @BaseExtractor.safe_extraction
    def is_symmetric(self) -> Optional[bool]:
        """
        Extracts whether the circular pattern is symmetric.

        Returns:
            Optional[bool]: True if symmetric, else False.
        """
        return self._obj.isSymmetric

    @property
    @BaseExtractor.safe_extraction
    def pattern_compute_option(self) -> Optional[str]:
        """
        Extracts the pattern compute option for the circular pattern feature.

        Returns:
            Optional[str]: The compute option type.
        """
        return self._obj.patternComputeOption

    @property
    @BaseExtractor.safe_extraction
    def suppressed_elements_ids(self) -> Optional[List[int]]:
        """
        Extracts the list of suppressed element IDs in the pattern.

        Returns:
            Optional[List[int]]: A list of suppressed element IDs.
        """
        return self._obj.suppressedElementsIds

    @property
    @BaseExtractor.safe_extraction
    def result_features(self) -> Optional[List[str]]:
        """
        Extracts the result features created by the circular pattern.

        Returns:
            Optional[List[str]]: A list of entity tokens for the result
            features.
        """
        result_features: adsk.core.ObjectCollection = self._obj.resultFeatures
        return [feature.entityToken for feature in result_features]

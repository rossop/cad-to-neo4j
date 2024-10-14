"""
Path Pattern Feature Extractor Module

This module provides an extractor class for extracting information from
PathPatternFeature objects.

Classes:
    - PathPatternFeatureExtractor: Extractor for PathPatternFeature objects.
"""

from typing import Optional, Any, Dict, List

import traceback

import adsk.fusion
import adsk.core

from .feature_extractor import FeatureExtractor

__all__ = ['PathPatternFeatureExtractor']


class PathPatternFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from PathPatternFeature
    objects."""

    def __init__(self, obj: adsk.fusion.PathPatternFeature):
        """
        Initialize the extractor with the PathPatternFeature element.

        Args:
            obj (adsk.fusion.PathPatternFeature): The PathPatternFeature object
                to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        """
        Extract all information from the PathPatternFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        pattern_info = {
            'inputEntities': self.input_entities,
            'path': self.path,
            'quantity': self.quantity,
            'distance': self.distance,
            'startPoint': self.start_point,
            'isFlipDirection': self.is_flip_direction,
            'isSymmetric': self.is_symmetric,
            'isOrientationAlongPath': self.is_orientation_along_path,
        }
        return {**feature_info, **pattern_info}

    @property
    def input_entities(self) -> Optional[List[str]]:
        """
        Extracts the input entities of the pattern.

        Returns:
            Optional[List[str]]: List of entity tokens for input entities.
        """
        try:
            input_entities = self._obj.inputEntities
            return [entity.entityToken
                    for entity in input_entities] if input_entities else []
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting input entities: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

    @property
    def path(self) -> Optional[str]:
        """
        Extracts the path used for the pattern.

        Returns:
            Optional[str]: The entity token of the path.
        """
        try:
            return self._obj.path.entityToken if self._obj.path else None
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting path: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

    @property
    def quantity(self) -> Optional[float]:
        """
        Extracts the number of instances along the path.

        Returns:
            Optional[float]: Number of instances.
        """
        try:
            return getattr(self._obj.quantity, 'value', None)
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting quantity: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

    @property
    def distance(self) -> Optional[float]:
        """
        Extracts the distance between the instances.

        Returns:
            Optional[float]: Distance between instances.
        """
        try:
            return getattr(self._obj.distance, 'value', None)
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting distance: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

    @property
    def start_point(self) -> Optional[float]:
        """
        Extracts the start point on the path.

        Returns:
            Optional[float]: Start point between 0 and 1.
        """
        try:
            return self._obj.startPoint
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting start point: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

    @property
    def is_flip_direction(self) -> Optional[bool]:
        """
        Extracts whether the pattern is flipped along the path.

        Returns:
            Optional[bool]: True if flipped, False otherwise.
        """
        try:
            return self._obj.isFlipDirection
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting flip direction: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

    @property
    def is_symmetric(self) -> Optional[bool]:
        """
        Extracts whether the pattern is symmetric.

        Returns:
            Optional[bool]: True if symmetric, False otherwise.
        """
        try:
            return self._obj.isSymmetric
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting symmetry: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

    @property
    def is_orientation_along_path(self) -> Optional[bool]:
        """
        Extracts whether the orientation is along the path.

        Returns:
            Optional[bool]: True if along the path, False otherwise.
        """
        try:
            return self._obj.isOrientationAlongPath
        except AttributeError as e:
            attribute_error_msg: str = (
                f"Error extracting orientation along path: {e}\n"
                f"{traceback.format_exc()}"
            )
            self.logger.error(attribute_error_msg)
            return None

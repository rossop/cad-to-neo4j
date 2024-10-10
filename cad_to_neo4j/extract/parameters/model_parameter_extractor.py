"""
Model Parameter Extractor Module

This module provides an extractor class for extracting information from ModelParameter objects.

Classes:
    - ModelParameterExtractor: Extractor for ModelParameter objects.
"""

from typing import Dict, Optional, Union
import adsk.fusion
from .parameter_extractor import ParameterExtractor


class ModelParameterExtractor(ParameterExtractor):
    """Extractor for extracting detailed information from ModelParameter objects."""

    def __init__(self, obj: adsk.fusion.ModelParameter) -> None:
        """
        Initializes the ModelParameterExtractor with a ModelParameter object.

        Args:
            obj (adsk.fusion.ModelParameter): The ModelParameter object to extract information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Union[str, float]]]:
        """
        Extracts model parameter information, including name, role, and value.

        Returns:
            Dict[str, Optional[Union[str, float]]]: A dictionary containing 
                                                    detailed information of the model parameter.
        """
        basic_info = super().extract_info()
        model_info = {
            'role': self._obj.role,
            'component': self._obj.component.name
        }
        return {**basic_info, **model_info}

    @property
    def created_by(self) -> str:
        """
        Returns the object that created this parameter, such as a feature or a sketch dimension.

        Returns:
            str: The name of the object that created the parameter.
        """
        return self._obj.createdBy.name

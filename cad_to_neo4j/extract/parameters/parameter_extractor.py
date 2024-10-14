"""
Parameter Extractor Module

This module provides extractors for extracting information from Parameter
Object

Classes:
    - ParameterExtractor: Extractor for generic Parameter objects."""

from typing import Dict, Optional, Union, List

import adsk.core
import adsk.fusion

from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import helper_extraction_error


class ParameterExtractor(BaseExtractor):
    """Extractor for extracting detailed information from Parameter objects."""

    def __init__(self, obj: adsk.fusion.Parameter) -> None:
        """
        Initializes the ParameterExtractor with a Parameter object.

        Args:
            obj (adsk.fusion.Parameter): The Parameter object to extract
                information from.
        """
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Optional[Union[str, float]]]:
        """
        Extracts parameter information, including name, expression, and value.

        Returns:
            Dict[str, Optional[Union[str, float]]]: A dictionary containing
            detailed information of the parameter.
        """
        base_info = super().extract_info()
        parameter_info = {
            'value': self._obj.value,
            'expression': self._obj.expression,
            'unit': self._obj.unit,
            'isFavorite': self._obj.isFavorite,
            'isDeletable': self._obj.isDeletable,
            'dependencyParameters': self.dependency_parameters,
            'dependentParameters': self.dependent_parameters,
        }
        return {**base_info, **parameter_info}

    @property
    @helper_extraction_error
    def dependent_parameters(self) -> List[str]:
        """
        Returns a list of parameters that are dependent on this parameter.

        Returns:
            list: A list of dependent parameters.
        """
        # return [param.name for param in self._obj.dependentParameters]
        return self.extract_collection_tokens('dependentParameters')

    @property
    @helper_extraction_error
    def dependency_parameters(self) -> List[str]:
        """
        Returns a list of parameters that this parameter is dependent on.

        Returns:
            list: A list of dependency parameters.
        """
        # return [param.name for param in self._obj.dependencyParameters]
        return self.extract_collection_tokens('dependencyParameters')

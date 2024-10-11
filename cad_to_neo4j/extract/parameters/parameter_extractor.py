"""
Parameter Extractor Module

This module provides extractors for extracting information from Parameter
Object

Classes:
    - ParameterExtractor: Extractor for generic Parameter objects."""

from typing import Dict, Optional, Union
import adsk.core
import adsk.fusion


class ParameterExtractor:
    """Extractor for extracting detailed information from Parameter objects."""

    def __init__(self, obj: adsk.fusion.Parameter) -> None:
        """
        Initializes the ParameterExtractor with a Parameter object.

        Args:
            obj (adsk.fusion.Parameter): The Parameter object to extract
                information from.
        """
        self._obj = obj

    def extract_info(self) -> Dict[str, Optional[Union[str, float]]]:
        """
        Extracts parameter information, including name, expression, and value.

        Returns:
            Dict[str, Optional[Union[str, float]]]: A dictionary containing
                                        detailed information of the parameter.
        """
        return {
            'name': self._obj.name,
            'value': self._obj.value,
            'expression': self._obj.expression,
            'unit': self._obj.unit,
            'isFavorite': self._obj.isFavorite,
            'isDeletable': self._obj.isDeletable
        }

    @property
    def entity_token(self) -> str:
        """
        Returns the entity token for the parameter.

        Returns:
            str: The entity token of the parameter.
        """
        return self._obj.entityToken

    @property
    def dependent_parameters(self) -> list:
        """
        Returns a list of parameters that are dependent on this parameter.

        Returns:
            list: A list of dependent parameters.
        """
        return [param.name for param in self._obj.dependentParameters]

    @property
    def dependency_parameters(self) -> list:
        """
        Returns a list of parameters that this parameter is dependent on.

        Returns:
            list: A list of dependency parameters.
        """
        return [param.name for param in self._obj.dependencyParameters]

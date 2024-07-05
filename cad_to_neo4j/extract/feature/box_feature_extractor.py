# box_feature_extractor.py
from typing import Optional, List
import adsk.fusion
import traceback
from .feature_extractor import FeatureExtractor

__all__ = ['BoxFeatureExtractor']

class BoxFeatureExtractor(FeatureExtractor):
    """Extractor for extracting detailed information from BoxFeature objects."""

    def __init__(self, obj: adsk.fusion.BoxFeature):
        """Initialize the extractor with the BoxFeature element."""
        super().__init__(obj)

    @property
    def length(self) -> Optional[float]:
        """Extracts the length of the box."""
        try:
            return self._obj.length.value
        except AttributeError as e:
            self.logger.error(f'Error extracting length: {e}\n{traceback.format_exc()}')
            return None

    @property
    def width(self) -> Optional[float]:
        """Extracts the width of the box."""
        try:
            return self._obj.width.value
        except AttributeError as e:
            self.logger.error(f'Error extracting width: {e}\n{traceback.format_exc()}')
            return None

    @property
    def height(self) -> Optional[float]:
        """Extracts the height of the box."""
        try:
            return self._obj.height.value
        except AttributeError as e:
            self.logger.error(f'Error extracting height: {e}\n{traceback.format_exc()}')
            return None

    def extract_info(self) -> dict:
        """Extract all information from the BoxFeature element.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        feature_info = super().extract_info()
        box_info = {
            # 'length': self.length,
            # 'width': self.width,
            # 'height': self.height,
        }
        TEXT = f''
        for m in dir(self._obj):
            val = getattr(self._obj,m,None)
            TEXT += f'{m} \n {val}\n\n' 

        self.logger.debug(TEXT)               
        return {**feature_info, **box_info}

# profile_curve_extractor.py
from typing import Dict, Any
from adsk.fusion import ProfileCurve
from ...base_extractor import BaseExtractor

from ....utils.general_utils import nested_getattr

class ProfileCurveExtractor(BaseExtractor):
    def __init__(self, obj: ProfileCurve):
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        base_info = super().extract_info()
        curve_info = {
            'geometryType': self.geometry_type,
            'sketchEntity': self.sketch_entity,
            'tempId' : None,
        }

        # Add geometry information if available
        geometry = self.geometry
        if geometry is not None:
            curve_info.update(geometry)
        return {**curve_info,**base_info}

    @property
    def geometry_type(self) -> str:
        return getattr(self._obj, 'geometryType', None)

    @property
    def geometry(self) -> Dict[str, Any]:
        geom = getattr(self._obj, 'geometry', None)
        if geom:
            return {
                'startPoint': [geom.startPoint.x, geom.startPoint.y, geom.startPoint.z],
                'endPoint': [geom.endPoint.x, geom.endPoint.y, geom.endPoint.z]
            }
        return {}

    @property
    def sketch_entity(self) -> str:
        # change tto the baseextractor formula
        return nested_getattr(self._obj, 'sketchEntity.entityToken', None)
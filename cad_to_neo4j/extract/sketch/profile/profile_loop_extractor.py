# profile_loop_extractor.py
import uuid
from typing import Dict, Any, Optional
from adsk.fusion import ProfileLoop
from ...base_extractor import BaseExtractor
from .profile_curve_extractor import ProfileCurveExtractor

class ProfileLoopExtractor(BaseExtractor):
    def __init__(self, obj: ProfileLoop):
        super().__init__(obj)

    def extract_info(self) -> Dict[str, Any]:
        base_info = super().extract_info()
        loop_info = {
            'isOuter': self.isOuter,
            'profileCurves': None,
            'tempId' : None,
        }

        # Add curveInfo if available
        curve_info = self.curveInfo
        if curve_info is not None:
            loop_info.update(curve_info)

        return {**base_info, **loop_info}

    @property
    def isOuter(self) -> bool:
        return getattr(self._obj, 'isOuter', None)

    @property
    def curveInfo(self) -> Optional[Dict[str,Any]]:
        try:
            curvesEntities = getattr(self._obj, 'profileCurves', [])
            profileCurves = []
            profileCurveEntities =[]
            for curve in curvesEntities:
                info = ProfileCurveExtractor(curve).extract_info()
                if info['tempId'] is None:
                    tempId = str(uuid.uuid4())
                    info['tempId'] = tempId
                    profileCurves.append(tempId)
                    profileCurveEntities.append(info)
            
            return {
                'profileCurveEntities' : profileCurveEntities,
                'profileCurves' : profileCurves,
            }
        except AttributeError:
            return None
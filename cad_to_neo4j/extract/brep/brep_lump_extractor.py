from typing import Dict, Any

import adsk.fusion  # TODO standardise this import for
from .brep_entity_extractor import BRepEntityExtractor

__all__ = ['BRepLumpExtractor']


class BRepLumpExtractor(BRepEntityExtractor):
    """Extractor for BRepLump data."""
    def __init__(self,
                 obj: adsk.fusion.BRepLump,
                 design_environment_data: Dict[str, Any]):
        """Initialize the extractor with the BRepLump element."""
        super().__init__(obj, design_environment_data=design_environment_data)

    def extract_info(self) -> dict:
        """Extract BRepLump data."""
        entity_info = super().extract_info()
        lump_info = {}
        return {**entity_info, **lump_info}

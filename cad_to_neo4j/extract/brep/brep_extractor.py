"""
BRepBody Extractor Module

This module provides an extractor class for extracting information from
Boundary Representations object including BRep entities such as faces,
edges, and vertices.

Classes:
    - BRepBodyExtractor: Extractor for BRepBody objects.
"""
import adsk.fusion

from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import nested_getattr
from ...utils.extraction_utils import helper_extraction_error

__all__ = ['BRepBodyExtractor']


class BRepBodyExtractor(BaseExtractor):
    """Extractor for BRepBody data from bodies and features."""
    def __init__(self,
                 obj: adsk.fusion.BRepBody):
        """Initialize the extractor with the BRepBody element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract BRepBody data."""
        basic_info = super().extract_info()

        brep_body_info = {
            'parent_component': self.parent_component,
            'isSolid': self.is_solid,
            'area': self.area,
            'volume': self.volume,
            'is_visible': self.is_visible,
            'is_selectable': self.is_selectable,
            # 'opacity': self.opacity,
            # 'visible_opacity': self.visible_opacity,
            'revision_id': self.revision_id,
            'entity_token': self.entity_token,
            'is_sheet_metal': self.is_sheet_metal,
            'concave_edges': self.concave_edges,
            'convex_edges': self.convex_edges,
            # 'lumps': self.lumps,
            # 'shells': self.shells,
            # 'faces': self.faces,
            # 'edges': self.edges,
            # 'vertices': self.vertices
        }

        bounding_box_info = self.bounding_box
        if bounding_box_info is not None:
            brep_body_info.update(bounding_box_info)

        return {**basic_info, **brep_body_info}

    @property
    @helper_extraction_error
    def parent_component(self) -> str:
        """Gets the name of the parent component of the BRepBody."""
        try:
            return nested_getattr(self._obj, 'parentComponent.name', None)
        except AttributeError:
            return None

    @property
    @helper_extraction_error
    def is_solid(self) -> bool:
        """Indicates if the BRepBody is solid."""
        return getattr(self._obj, 'isSolid', None)

    @property
    @helper_extraction_error
    def bounding_box(self) -> dict:
        """Gets the bounding box of the BRepBody."""
        bounding_box = getattr(self._obj, 'boundingBox', None)
        if bounding_box:
            min_point = bounding_box.minPoint
            max_point = bounding_box.maxPoint
            return {
                'min_point': [min_point.x, min_point.y, min_point.z],
                'max_point': [max_point.x, max_point.y, max_point.z]
            }

    @property
    @helper_extraction_error
    def area(self) -> float:
        """Gets the area of the BRepBody."""
        return getattr(self._obj, 'area', None)

    @property
    @helper_extraction_error
    def volume(self) -> float:
        """Gets the volume of the BRepBody."""
        return getattr(self._obj, 'volume', None)

    @property
    @helper_extraction_error
    def is_visible(self) -> bool:
        """Indicates if the BRepBody is visible."""
        return getattr(self._obj, 'isVisible', None)

    @property
    @helper_extraction_error
    def is_selectable(self) -> bool:
        """Indicates if the BRepBody is selectable."""
        return getattr(self._obj, 'isSelectable', None)

    @property
    @helper_extraction_error
    def opacity(self) -> float:
        """Gets the opacity of the BRepBody."""
        return getattr(self._obj, 'opacity', None)

    @property
    @helper_extraction_error
    def visible_opacity(self) -> float:
        """Gets the visible opacity of the BRepBody."""
        return getattr(self._obj, 'visibleOpacity', None)

    @property
    @helper_extraction_error
    def revision_id(self) -> str:
        """Gets the revision ID of the BRepBody."""
        return getattr(self._obj, 'revisionId', None)

    @property
    @helper_extraction_error
    def entity_token(self) -> str:
        """Gets the entity token of the BRepBody."""
        return getattr(self._obj, 'entityToken', None)

    @property
    @helper_extraction_error
    def is_sheet_metal(self) -> bool:
        """Indicates if the BRepBody represents a sheet metal part."""
        return getattr(self._obj, 'isSheetMetal', None)

    @property
    @helper_extraction_error
    def concave_edges(self) -> list:
        """Returns all the concave edges' identity tokens in the BRepBody."""
        concave_edges = getattr(self._obj, 'concaveEdges', None)
        if concave_edges:
            return [edge.entityToken for edge in concave_edges
                    if getattr(edge, 'entityToken', None) is not None]

    @property
    @helper_extraction_error
    def convex_edges(self) -> list:
        """Returns all the convex edges' identity tokens in the BRepBody."""
        convex_edges = getattr(self._obj, 'convexEdges', None)
        if convex_edges:
            return [edge.entityToken for edge in convex_edges
                    if getattr(edge, 'entityToken', None) is not None]

    @property
    @helper_extraction_error
    def lumps(self) -> list:
        """Returns all the lumps' identity tokens in the BRepBody."""
        return self.extract_collection_tokens('lumps', 'entityToken')

    @property
    @helper_extraction_error
    def shells(self) -> list:
        """Returns all the shells' identity tokens in the BRepBody."""
        return self.extract_collection_tokens('shells', 'entityToken')

    @property
    @helper_extraction_error
    def faces(self) -> list:
        """Returns all the faces' identity tokens in the BRepBody."""
        return self.extract_collection_tokens('faces', 'entityToken')

    @property
    @helper_extraction_error
    def edges(self) -> list:
        """Returns all the edges' identity tokens in the BRepBody."""
        return self.extract_collection_tokens('edges', 'entityToken')

    @property
    @helper_extraction_error
    def vertices(self) -> list:
        """Returns all the vertices' identity tokens in the BRepBody."""
        return self.extract_collection_tokens('vertices', 'entityToken')

    # @property
    # def material(self) -> dict:
    #     """Gets the material of the BRepBody."""
    #     try:
    #         material = self._obj.material
    #         if material:
    #             return {
    #                 'name': material.name,
    #                 'id': material.id
    #             }
    #     except AttributeError:
    #         return None

"""
BRepBody Extractor Module

This module provides an extractor class for extracting information from 
Boundary Representations object including BRep entities such as faces, 
edges, and vertices.

Classes:
    - BRepBodyExtractor: Extractor for BRepBody objects.
"""
import adsk.core as core
import adsk.fusion # TODO standardise this import for 
from ..base_extractor import BaseExtractor
from ...utils.extraction_utils import nested_getattr

__all__ = ['BRepBodyExtractor']

# TODO consider importing from BRepEntity
class BRepBodyExtractor(BaseExtractor):
    """Extractor for BRepBody data from bodies and features."""
    def __init__(self, obj: adsk.fusion.BRepBody):
        """Initialize the extractor with the BRepBody element."""
        super().__init__(obj)

    def extract_info(self) -> dict:
        """Extract BRepBody data."""
        basic_info = super().extract_info()
        
        brep_body_info = {
            'parent_component': self.parent_component,
            'isSolid': self.isSolid,
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
    def parent_component(self) -> str:
        """Gets the name of the parent component of the BRepBody."""
        try:
            return nested_getattr(self._obj, 'parentComponent.name', None)
        except AttributeError:
            return None

    @property
    def isSolid(self) -> bool:
        """Indicates if the BRepBody is solid."""
        try:
            return getattr(self._obj,'isSolid', None)
        except AttributeError:
            return None

    @property
    def bounding_box(self) -> dict:
        """Gets the bounding box of the BRepBody."""
        try:
            bounding_box = getattr(self._obj,'boundingBox', None)
            if bounding_box:
                minPoint = bounding_box.minPoint
                maxPoint = bounding_box.maxPoint
                return {
                    'min_point': [minPoint.x, minPoint.y, minPoint.z],
                    'max_point': [maxPoint.x, maxPoint.y, maxPoint.z]
                }
        except AttributeError:
            return None

    @property
    def area(self) -> float:
        """Gets the area of the BRepBody."""
        try:
            return getattr(self._obj,'area', None)
        except AttributeError:
            return None

    @property
    def volume(self) -> float:
        """Gets the volume of the BRepBody."""
        try:
            return getattr(self._obj,'volume',None)
        except AttributeError:
            return None

    @property
    def is_visible(self) -> bool:
        """Indicates if the BRepBody is visible."""
        try:
            return getattr(self._obj,'isVisible', None)
        except AttributeError:
            return None

    @property
    def is_selectable(self) -> bool:
        """Indicates if the BRepBody is selectable."""
        try:
            return getattr(self._obj,'isSelectable', None)
        except AttributeError:
            return None


    @property
    def opacity(self) -> float:
        """Gets the opacity of the BRepBody."""
        try:
            return getattr(self._obj,'opacity', None)
        except AttributeError:
            return None

    @property
    def visible_opacity(self) -> float:
        """Gets the visible opacity of the BRepBody."""
        try:
            return getattr(self._obj,'visibleOpacity', None)
        except AttributeError:
            return None

    @property
    def revision_id(self) -> str:
        """Gets the revision ID of the BRepBody."""
        try:
            return getattr(self._obj,'revisionId', None)
        except AttributeError:
            return None

    @property
    def entity_token(self) -> str:
        """Gets the entity token of the BRepBody."""
        try:
            return getattr(self._obj,'entityToken', None)
        except AttributeError:
            return None

    @property
    def is_sheet_metal(self) -> bool:
        """Indicates if the BRepBody represents a sheet metal part."""
        try:
            return getattr(self._obj, 'isSheetMetal', None)
        except AttributeError:
            return None

    @property
    def concave_edges(self) -> list:
        """Returns all the concave edges' identity tokens in the BRepBody."""
        try:
            concave_edges = getattr(self._obj, 'concaveEdges', None)
            if concave_edges:
                return [edge.entityToken for edge in concave_edges 
                        if getattr(edge, 'entityToken', None) is not None]
        except AttributeError:
            return []
        return []

    @property
    def convex_edges(self) -> list:
        """Returns all the convex edges' identity tokens in the BRepBody."""
        try:
            convex_edges = getattr(self._obj, 'convexEdges', None)
            if convex_edges:
                return [edge.entityToken for edge in convex_edges 
                        if getattr(edge, 'entityToken', None) is not None]
        except AttributeError:
            return []
        return []

    @property
    def lumps(self) -> list:
        """Returns all the lumps' identity tokens in the BRepBody."""
        try:
            lumps = getattr(self._obj, 'lumps', None)
            if lumps:
                return [lump.entityToken for lump in lumps] # if getattr(lump, 'entityToken', None) is not None]
        except AttributeError:
            return []
        return []

    @property
    def shells(self) -> list:
        """Returns all the shells' identity tokens in the BRepBody."""
        try:
            shells = getattr(self._obj, 'shells', None)
            if shells:
                return [shell.entityToken for shell in shells if getattr(shell, 'entityToken', None) is not None]
        except AttributeError:
            return []
        return []

    @property
    def faces(self) -> list:
        """Returns all the faces' identity tokens in the BRepBody."""
        try:
            faces = getattr(self._obj, 'faces', None)
            if faces:
                return [face.entityToken for face in faces if getattr(face, 'entityToken', None) is not None]
        except AttributeError:
            return []
        return []

    @property
    def edges(self) -> list:
        """Returns all the edges' identity tokens in the BRepBody."""
        try:
            edges = getattr(self._obj, 'edges', None)
            if edges:
                return [edge.entityToken for edge in edges if getattr(edge, 'entityToken', None) is not None]
        except AttributeError:
            return []
        return []

    @property
    def vertices(self) -> list:
        """Returns all the vertices' identity tokens in the BRepBody."""
        try:
            vertices = getattr(self._obj, 'vertices', None)
            if vertices:
                return [vertex.entityToken for vertex in vertices if getattr(vertex, 'entityToken', None) is not None]
        except AttributeError:
            return []
        return []
    
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

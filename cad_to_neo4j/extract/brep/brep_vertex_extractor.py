import adsk.fusion # TODO standardise this import for 
from .brep_entity_extractor import BRepEntityExtractor

__all__ = ['BRepVertexExtractor']

class BRepVertexExtractor(BRepEntityExtractor):
    """
    Extractor for BRepVertex data.
    """
    def __init__(self, obj: adsk.fusion.BRepVertex):
        """
        Initialize the BRepVertexExtractor with a BRepVertex object.

        Args:
            obj (adsk.fusion.BRepVertex): The BRepVertex object to extract data from.
        """
        super().__init__(obj)

    def extract_info(self) -> dict:
        """
        Extract information from the BRepVertex object.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        entity_info = super().extract_info()
        vertex_info = {
            'isTolerant': self.isTolerant,
            'tolerance': self.tolerance,
            'geometry': self.geometry,
            # 'shell': self.shell,
        }
        return {**entity_info, **vertex_info}

    @property
    def isTolerant(self):
        """
        Check if the vertex is tolerant.

        Returns:
            bool: True if the vertex is tolerant, else False.
        """
        try:
            return getattr(self._obj, 'isTolerant', None)
        except Exception as e:
            self.logger.error(f"Error extracting isTolerant: {e}")
            return None

    @property
    def tolerance(self):
        """
        Extract the tolerance value of the vertex.

        Returns:
            float: The tolerance value.
        """
        try:
            return getattr(self._obj, 'tolerance', None)
        except Exception as e:
            self.logger.error(f"Error extracting tolerance: {e}")
            return None

    @property
    def geometry(self):
        """
        Extract the geometry of the vertex.

        Returns:
            list: Coordinates of the vertex [x, y, z].
        """
        try:
            geometry = getattr(self._obj, 'geometry', None)
            return [geometry.x, geometry.y, geometry.z] if geometry else None
        except Exception as e:
            self.logger.error(f"Error extracting geometry: {e}")
            return None

    @property
    def shell(self):
        """
        Extract the shell associated with the vertex.

        Returns:
            str: Entity token of the associated shell.
        """
        try:
            shell = getattr(self._obj, 'shell', None)
            return getattr(shell, 'entityToken', None)
        except Exception as e:
            self.logger.error(f"Error extracting shell: {e}")
            return None
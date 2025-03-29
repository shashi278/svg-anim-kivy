"""
Mesh generation and handling for SVG shapes.
"""
from kivy.graphics import Mesh as KivyMesh, Color
from kivy.graphics.tesselator import Tesselator, WINDING_ODD, TYPE_POLYGONS
from typing import List, Tuple, Any

class MeshHandler:
    """Handler for mesh generation and rendering of SVG paths."""
    
    @staticmethod
    def create_tesselator(shapes: List[List[float]]) -> Tesselator:
        """
        Create a tesselator for the given shapes.
        
        Args:
            shapes: List of shapes represented as lists of points
            
        Returns:
            Tesselator object with added contours
        """
        tess = Tesselator()
        for shape in shapes:
            if len(shape) >= 3:
                tess.add_contour(shape)
        return tess
        
    @staticmethod
    def generate_meshes(shapes: List[List[float]]) -> List[Tuple[List[float], List[int]]]:
        """
        Generate meshes from the given shapes.
        
        Args:
            shapes: List of shapes represented as lists of points
            
        Returns:
            List of (vertices, indices) tuples for mesh rendering
        """
        tess = MeshHandler.create_tesselator(shapes)
        tess.tesselate(WINDING_ODD, TYPE_POLYGONS)
        return tess.meshes
    
    @staticmethod
    def render_mesh(widget, shapes: List[List[float]], color: List[float], opacity_attr: str) -> None:
        """
        Render meshes onto the given canvas.
        
        Args:
            widget: Widget that contains the canvas to render on
            shapes: List of shapes represented as lists of points
            color: RGB color values [r, g, b]
            opacity_attr: Name of the attribute containing opacity value
            
        Returns:
            None
        """
        meshes = MeshHandler.generate_meshes(shapes)
        # Get the opacity value, using 1.0 as a default if the attribute doesn't exist
        opacity = getattr(widget, opacity_attr, 1.0)

        with widget.canvas:
            Color(*color[:3], opacity)
            for vertices, indices in meshes:
                KivyMesh(vertices=vertices, indices=indices, mode="triangle_fan")

"""
SVG rendering functionality for Kivg.
"""
from kivy.graphics import Line as KivyLine, Color
from svg.path.path import Line, CubicBezier, Close, Move
from typing import Dict, List, Tuple, Any, Optional

from .path_utils import get_all_points

class SvgRenderer:
    """Handles rendering of SVG paths to Kivy canvas."""
    
    @staticmethod
    def update_canvas(widget, path_elements: List[Line | CubicBezier], line_color: List[float]) -> None:
        """
        Update the canvas with the current path elements.
        
        Args:
            widget: Widget to draw on
            path_elements: List of SVG path elements
            line_color: Color to use for drawing lines
            
        Returns:
            None
        """
        widget.canvas.clear()
        
        with widget.canvas:
            Color(*line_color)
            
            line_count = 0
            bezier_count = 0
            
            # Draw each path element
            for element in path_elements:
                if isinstance(element, Line):
                    SvgRenderer._draw_line(widget, line_count)
                    line_count += 1
                    
                elif isinstance(element, CubicBezier):
                    SvgRenderer._draw_bezier(widget, bezier_count)
                    bezier_count += 1
    
    @staticmethod
    def _draw_line(widget, line_index: int) -> None:
        """Draw a line element on the canvas."""
        KivyLine(
            points=[
                getattr(widget, f"line{line_index}_start_x"),
                getattr(widget, f"line{line_index}_start_y"),
                getattr(widget, f"line{line_index}_end_x"),
                getattr(widget, f"line{line_index}_end_y"),
            ],
            width=getattr(widget, f"line{line_index}_width"),
        )
    
    @staticmethod
    def _draw_bezier(widget, bezier_index: int) -> None:
        """Draw a bezier curve element on the canvas."""
        KivyLine(
            bezier=[
                getattr(widget, f"bezier{bezier_index}_start_x"),
                getattr(widget, f"bezier{bezier_index}_start_y"),
                getattr(widget, f"bezier{bezier_index}_control1_x"),
                getattr(widget, f"bezier{bezier_index}_control1_y"),
                getattr(widget, f"bezier{bezier_index}_control2_x"),
                getattr(widget, f"bezier{bezier_index}_control2_y"),
                getattr(widget, f"bezier{bezier_index}_end_x"),
                getattr(widget, f"bezier{bezier_index}_end_y"),
            ],
            width=getattr(widget, f"bezier{bezier_index}_width"),
        )
    
    @staticmethod
    def collect_shape_points(tmp_elements_lists, widget, shape_id) -> List[float]:
        """
        Collect all current points for a shape during animation.
        
        Args:
            tmp_elements_lists: Path data from shape_animate
            widget: Widget containing animation properties
            shape_id: ID of the shape
            
        Returns:
            List of points representing the current shape state
        """
        shape_list = []
        line_count = 0
        bezier_count = 0

        for path_elements in tmp_elements_lists:
            for element in path_elements:
                # Collect line points
                if len(element) == 2:  # Line
                    shape_list.extend([
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_start_x"),
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_start_y"),
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_end_x"),
                        getattr(widget, f"{shape_id}_mesh_line{line_count}_end_y")
                    ])
                    line_count += 1
                
                # Collect bezier points
                if len(element) == 4:  # Bezier
                    shape_list.extend(
                        get_all_points(
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_start_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_start_y")),
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control1_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control1_y")),
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control2_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_control2_y")),
                            (getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_end_x"),
                             getattr(widget, f"{shape_id}_mesh_bezier{bezier_count}_end_y"))
                        )
                    )
                    bezier_count += 1
        return shape_list

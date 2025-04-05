"""
DrawingManager handles SVG path processing and rendering preparation.
"""

from collections import OrderedDict
from typing import List, Tuple, Dict, Any, Optional

from svg.path import parse_path
from svg.path.path import Line, CubicBezier, Close, Move

from ..animation.kivy_animation import Animation
from ..path_utils import get_all_points, bezier_points, line_points
from ..svg_parser import parse_svg


class DrawingManager:
    """Handles the drawing and rendering of SVG paths."""
    
    @staticmethod
    def process_path_data(svg_file: str) -> Tuple[List[float], OrderedDict, List]:
        """
        Process SVG file and extract path data.
        
        Args:
            svg_file: Path to the SVG file
            
        Returns:
            Tuple of (svg_dimensions, closed_shapes, path_elements)
        """
        sw_size, path_strings = parse_svg(svg_file)
        
        path = []
        closed_shapes = OrderedDict()
        
        for path_string, id_, clr in path_strings:
            move_found = False
            tmp = []
            closed_shapes[id_] = dict()
            closed_shapes[id_][id_ + "paths"] = []
            closed_shapes[id_][id_ + "shapes"] = []  # for drawing meshes
            closed_shapes[id_]["color"] = clr
            
            _path = parse_path(path_string)
            for e in _path:
                path.append(e)

                if isinstance(e, Close) or (isinstance(e, Move) and move_found):
                    closed_shapes[id_][id_ + "paths"].append(tmp)
                    move_found = False

                if isinstance(e, Move):  # shape started
                    tmp = []
                    move_found = True

                if not isinstance(e, Move) and move_found:
                    tmp.append(e)
        
        return sw_size, closed_shapes, path

    @staticmethod
    def calculate_paths(
        widget: Any,
        closed_shapes: OrderedDict,
        svg_size: List[float],
        svg_file: str,
        animate: bool = False,
        line_width: int = 2,
        duration: float = 0.02
    ) -> List[Animation]:
        """
        Calculate and set up path properties for rendering.
        
        Args:
            widget: Widget to draw on
            closed_shapes: Path data organized by shape ID
            svg_size: SVG dimensions [width, height]
            svg_file: SVG file path
            animate: Whether to animate the drawing
            line_width: Width of the drawn lines
            duration: Duration for each animation step
            
        Returns:
            List of Animation objects if animate=True
        """
        line_count = 0
        bezier_count = 0
        anim_list = []
        
        for id_, closed_paths in closed_shapes.items():
            for s in closed_paths[id_ + "paths"]:
                tmp = []
                for e in s:
                    if isinstance(e, Line):
                        lp = line_points(
                            e, [*widget.size], [*widget.pos], [*svg_size], svg_file
                        )
                        DrawingManager._setup_line_properties(
                            widget, line_count, lp, animate, line_width
                        )

                        if animate:
                            anim_list.append(
                                Animation(
                                    d=duration,
                                    **{
                                        f"line{line_count}_end_x": lp[2],
                                        f"line{line_count}_end_y": lp[3],
                                        f"line{line_count}_width": line_width
                                    }
                                )
                            )
                        line_count += 1
                        tmp.extend(lp)
                        
                    elif isinstance(e, CubicBezier):
                        bp = bezier_points(
                            e, [*widget.size], [*widget.pos], [*svg_size], svg_file
                        )
                        DrawingManager._setup_bezier_properties(
                            widget, bezier_count, bp, animate, line_width
                        )

                        if animate:
                            anim_list.append(
                                Animation(
                                    d=duration,
                                    **{
                                        f"bezier{bezier_count}_control1_x": bp[2],
                                        f"bezier{bezier_count}_control1_y": bp[3],
                                        f"bezier{bezier_count}_control2_x": bp[4],
                                        f"bezier{bezier_count}_control2_y": bp[5],
                                        f"bezier{bezier_count}_end_x": bp[6],
                                        f"bezier{bezier_count}_end_y": bp[7],
                                        f"bezier{bezier_count}_width": line_width
                                    }
                                )
                            )
                        bezier_count += 1

                        tmp.extend(
                            get_all_points(
                                (bp[0], bp[1]),
                                (bp[2], bp[3]),
                                (bp[4], bp[5]),
                                (bp[6], bp[7]),
                            )
                        )

                if tmp not in closed_paths[id_ + "shapes"]:
                    closed_paths[id_ + "shapes"].append(tmp)
        
        return anim_list
    
    @staticmethod
    def _setup_line_properties(widget: Any, line_index: int, 
                              line_points: List[float], animate: bool, 
                              line_width: int) -> None:
        """Set up line properties on the widget."""
        setattr(widget, f"line{line_index}_start_x", line_points[0])
        setattr(widget, f"line{line_index}_start_y", line_points[1])
        setattr(
            widget,
            f"line{line_index}_end_x",
            line_points[0] if animate else line_points[2],
        )
        setattr(
            widget,
            f"line{line_index}_end_y",
            line_points[1] if animate else line_points[3],
        )
        setattr(
            widget,
            f"line{line_index}_width",
            1 if animate else line_width,
        )
    
    @staticmethod
    def _setup_bezier_properties(widget: Any, bezier_index: int, 
                                bezier_points: List[float], animate: bool, 
                                line_width: int) -> None:
        """Set up bezier curve properties on the widget."""
        # Start point
        setattr(widget, f"bezier{bezier_index}_start_x", bezier_points[0])
        setattr(widget, f"bezier{bezier_index}_start_y", bezier_points[1])
        
        # Control points
        setattr(
            widget,
            f"bezier{bezier_index}_control1_x",
            bezier_points[0] if animate else bezier_points[2],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_control1_y",
            bezier_points[1] if animate else bezier_points[3],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_control2_x",
            bezier_points[0] if animate else bezier_points[4],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_control2_y",
            bezier_points[1] if animate else bezier_points[5],
        )
        
        # End point
        setattr(
            widget,
            f"bezier{bezier_index}_end_x",
            bezier_points[0] if animate else bezier_points[6],
        )
        setattr(
            widget,
            f"bezier{bezier_index}_end_y",
            bezier_points[1] if animate else bezier_points[7],
        )
        
        # Width
        setattr(
            widget,
            f"bezier{bezier_index}_width",
            1 if animate else line_width,
        )
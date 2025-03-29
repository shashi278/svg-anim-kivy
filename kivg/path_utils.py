"""
Path utilities for Kivg.
Contains functions to convert SVG paths to Kivy-compatible coordinates.
"""
from typing import Tuple, List, Union, Callable
import math
from svg.path.path import Line, CubicBezier

def transform_x(x_pos: float, widget_x: float, widget_width: float, 
               svg_width: float, svg_file: str) -> float:
    """
    Transform an X coordinate from SVG to Kivy coordinate system.
    
    Args:
        x_pos: SVG x coordinate
        widget_x: Widget x position
        widget_width: Widget width
        svg_width: SVG width
        svg_file: SVG file path (for special kivy icon handling)
        
    Returns:
        Transformed x coordinate
    """
    # Special handling for Kivy SVG icons
    if "kivy" in svg_file:
        return widget_x + (widget_width * (x_pos / 10) / svg_width)
    return widget_x + widget_width * x_pos / svg_width

def transform_y(y_pos: float, widget_y: float, widget_height: float, 
               svg_height: float, svg_file: str) -> float:
    """
    Transform a Y coordinate from SVG to Kivy coordinate system.
    
    Args:
        y_pos: SVG y coordinate
        widget_y: Widget y position
        widget_height: Widget height
        svg_height: SVG height
        svg_file: SVG file path (for special kivy icon handling)
        
    Returns:
        Transformed y coordinate
    """
    # Special handling for Kivy SVG icons
    if "kivy" in svg_file:
        return widget_y + (widget_height * (y_pos / 10) / svg_height)
    return widget_y + widget_height * (svg_height - y_pos) / svg_height

def transform_point(complex_point: complex, widget_size: Tuple[float, float], 
                   widget_pos: Tuple[float, float], svg_size: Tuple[float, float], 
                   svg_file: str) -> List[float]:
    """
    Transform a complex point from SVG to Kivy coordinate system.
    
    Args:
        complex_point: SVG point as complex number
        widget_size: (width, height) of widget
        widget_pos: (x, y) of widget
        svg_size: (width, height) of SVG
        svg_file: SVG file path
        
    Returns:
        [x, y] transformed coordinates
    """
    w, h = widget_size
    wx, wy = widget_pos
    sw, sh = svg_size
    
    return [
        transform_x(complex_point.real, wx, w, sw, svg_file),
        transform_y(complex_point.imag, wy, h, sh, svg_file)
    ]

def bezier_points(bezier: CubicBezier, widget_size: Tuple[float, float], 
                 widget_pos: Tuple[float, float], svg_size: Tuple[float, float], 
                 svg_file: str) -> List[float]:
    """
    Convert a CubicBezier to Kivy-compatible bezier points.
    
    Args:
        bezier: CubicBezier object
        widget_size: (width, height) of widget
        widget_pos: (x, y) of widget
        svg_size: (width, height) of SVG
        svg_file: SVG file path
        
    Returns:
        List of points [x1, y1, cx1, cy1, cx2, cy2, x2, y2]
    """
    return [
        *transform_point(bezier.start, widget_size, widget_pos, svg_size, svg_file),
        *transform_point(bezier.control1, widget_size, widget_pos, svg_size, svg_file),
        *transform_point(bezier.control2, widget_size, widget_pos, svg_size, svg_file),
        *transform_point(bezier.end, widget_size, widget_pos, svg_size, svg_file),
    ]

def line_points(line: Line, widget_size: Tuple[float, float], 
               widget_pos: Tuple[float, float], svg_size: Tuple[float, float], 
               svg_file: str) -> List[float]:
    """
    Convert a Line to Kivy-compatible line points.
    
    Args:
        line: Line object
        widget_size: (width, height) of widget
        widget_pos: (x, y) of widget
        svg_size: (width, height) of SVG
        svg_file: SVG file path
        
    Returns:
        List of points [x1, y1, x2, y2]
    """
    return [
        *transform_point(line.start, widget_size, widget_pos, svg_size, svg_file),
        *transform_point(line.end, widget_size, widget_pos, svg_size, svg_file),
    ]

# Bernstein polynomials for Bezier calculation
# https://stackoverflow.com/a/15399173/8871954
B0_t = lambda t: (1 - t) ** 3
B1_t = lambda t: 3 * t * (1 - t) ** 2
B2_t = lambda t: 3 * t ** 2 * (1 - t)
B3_t = lambda t: t ** 3

def get_all_points(start: Tuple[float, float], control1: Tuple[float, float], 
                  control2: Tuple[float, float], end: Tuple[float, float], 
                  segments: int = 40) -> List[float]:
    """
    Generate discrete points along a cubic bezier curve.
    
    Args:
        start: Starting point (x, y)
        control1: First control point (x, y)
        control2: Second control point (x, y)
        end: End point (x, y)
        segments: Number of segments to generate
    
    Returns:
        Flattened list of points [x1, y1, x2, y2, ...]
    """
    points = []
    ax, ay = start
    bx, by = control1
    cx, cy = control2
    dx, dy = end

    seg = 1 / segments
    t = 0

    while t <= 1:
        points.extend([
            (B0_t(t) * ax) + (B1_t(t) * bx) + (B2_t(t) * cx) + (B3_t(t) * dx),
            (B0_t(t) * ay) + (B1_t(t) * by) + (B2_t(t) * cy) + (B3_t(t) * dy),
        ])
        t += seg

    return points

def find_center(sorted_list: List[float]) -> float:
    """
    Find the center value of a sorted list.
    
    Args:
        sorted_list: A sorted list of numbers
        
    Returns:
        The center value or average of the two middle values
    """
    middle = float(len(sorted_list)) / 2
    if middle % 2 != 0:
        return sorted_list[int(middle - 0.5)]
    else:
        return (sorted_list[int(middle)] + sorted_list[int(middle - 1)]) / 2

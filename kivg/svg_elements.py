"""
SVG Elements support for Kivg.
Provides classes and utilities to handle various SVG elements.
"""
from typing import List, Tuple, Dict, Any, Union
import math
from kivy.graphics import Line as KivyLine, Ellipse as KivyEllipse, Rectangle as KivyRectangle, RoundedRectangle
from kivy.graphics import Color


class SVGElement:
    """Base class for SVG elements."""

    def __init__(self, element_id: str = None, fill: List[float] = None, 
                 stroke: List[float] = None, stroke_width: float = 1.0):
        """
        Initialize an SVG element.
        
        Args:
            element_id: Identifier for the element
            fill: Fill color as [r, g, b, a] or None for no fill
            stroke: Stroke color as [r, g, b, a] or None for no stroke
            stroke_width: Width of the stroke
        """
        self.id = element_id
        self.fill = fill if fill is not None else [0, 0, 0, 1]
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.transform = None

    def get_points(self, widget_size: Tuple[float, float], 
                  widget_pos: Tuple[float, float], 
                  svg_size: Tuple[float, float]) -> List[float]:
        """
        Get points for the element transformed to widget coordinates.
        
        Args:
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
            
        Returns:
            List of transformed points
        """
        raise NotImplementedError("Subclasses must implement get_points")
    
    def render(self, canvas, widget_size: Tuple[float, float], 
              widget_pos: Tuple[float, float], 
              svg_size: Tuple[float, float]) -> None:
        """
        Render the element to a canvas.
        
        Args:
            canvas: Kivy canvas to render to
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
        """
        raise NotImplementedError("Subclasses must implement render")


class Circle(SVGElement):
    """Circle SVG element."""
    
    def __init__(self, cx: float, cy: float, r: float, **kwargs):
        """
        Initialize a circle element.
        
        Args:
            cx: X coordinate of the center
            cy: Y coordinate of the center
            r: Radius of the circle
            **kwargs: Additional arguments passed to SVGElement
        """
        super().__init__(**kwargs)
        self.cx = cx
        self.cy = cy
        self.r = r
    
    def get_points(self, widget_size: Tuple[float, float], 
                  widget_pos: Tuple[float, float], 
                  svg_size: Tuple[float, float]) -> List[float]:
        """
        Get points for the circle transformed to widget coordinates.
        
        For a circle, we return the center point and radius.
        
        Args:
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
            
        Returns:
            [center_x, center_y, radius]
        """
        from kivg.path_utils import transform_x, transform_y
        
        w, h = widget_size
        wx, wy = widget_pos
        sw, sh = svg_size
        
        # Transform center coordinates
        center_x = transform_x(self.cx, wx, w, sw, "")
        center_y = transform_y(self.cy, wy, h, sh, "")
        
        # Transform radius (average of x and y scaling)
        x_scale = w / sw
        y_scale = h / sh
        radius = self.r * (x_scale + y_scale) / 2
        
        return [center_x, center_y, radius]
    
    def render(self, canvas, widget_size: Tuple[float, float], 
              widget_pos: Tuple[float, float], 
              svg_size: Tuple[float, float]) -> None:
        """
        Render the circle to a canvas.
        
        Args:
            canvas: Kivy canvas to render to
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
        """
        points = self.get_points(widget_size, widget_pos, svg_size)
        center_x, center_y, radius = points

        print("points", points)
        
        with canvas:
            # Draw fill if specified
            if self.fill and self.fill[3] > 0:
                Color(*self.fill)
                KivyEllipse(pos=(center_x - radius, center_y - radius), 
                            size=(radius * 2, radius * 2))
            
            # Draw stroke if specified
            if self.stroke and self.stroke[3] > 0:
                Color(*self.stroke)
                KivyLine(circle=(center_x, center_y, radius), 
                         width=self.stroke_width)


class Rectangle(SVGElement):
    """Rectangle SVG element."""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 rx: float = 0, ry: float = 0, **kwargs):
        """
        Initialize a rectangle element.
        
        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            width: Width of the rectangle
            height: Height of the rectangle
            rx: X radius of the rounded corners (0 for no rounding)
            ry: Y radius of the rounded corners (0 for no rounding)
            **kwargs: Additional arguments passed to SVGElement
        """
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry
    
    def get_points(self, widget_size: Tuple[float, float], 
                  widget_pos: Tuple[float, float], 
                  svg_size: Tuple[float, float]) -> List[float]:
        """
        Get points for the rectangle transformed to widget coordinates.
        
        Args:
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
            
        Returns:
            [x, y, width, height, rx, ry]
        """
        from kivg.path_utils import transform_x, transform_y
        
        w, h = widget_size
        wx, wy = widget_pos
        sw, sh = svg_size
        
        # Transform position
        x = transform_x(self.x, wx, w, sw, "")
        y = transform_y(self.y, wy, h, sh, "")  # Convert from SVG coordinates
        
        # Transform size
        width = self.width * (w / sw)
        height = self.height * (h / sh)
        
        # Transform corner radii
        rx = self.rx * (w / sw)
        ry = self.ry * (h / sh)
        
        return [x, y - height, width, height, rx, ry]
    
    def render(self, canvas, widget_size: Tuple[float, float], 
              widget_pos: Tuple[float, float], 
              svg_size: Tuple[float, float]) -> None:
        """
        Render the rectangle to a canvas.
        
        Args:
            canvas: Kivy canvas to render to
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
        """
        points = self.get_points(widget_size, widget_pos, svg_size)
        print("widget_size", widget_size)
        print('rect points', points)
        x, y, width, height, rx, ry = points
        
        with canvas:
            # Draw fill if specified
            if self.fill and self.fill[3] > 0:
                Color(*self.fill)
                if rx > 0 or ry > 0:
                    # Draw a rounded rectangle
                    rounded_radius = min(rx, ry)
                    RoundedRectangle(
                        pos=(x, y),
                        size=(width, height),
                        radius=[rounded_radius,]
                    )
                else:
                    # Regular rectangle
                    KivyRectangle(pos=(x, y), size=(width, height))
            
            # Draw stroke if specified
            if self.stroke and self.stroke[3] > 0:
                Color(*self.stroke)
                if rx > 0 or ry > 0:
                    # Draw a rounded rectangle outline
                    corner_radius = min(rx, ry)
                    KivyLine(rounded_rectangle=(x, y, width, height, corner_radius),
                            width=self.stroke_width)
                else:
                    # Regular rectangle outline
                    KivyLine(rectangle=(x, y, width, height),
                            width=self.stroke_width)


class Ellipse(SVGElement):
    """Ellipse SVG element."""
    
    def __init__(self, cx: float, cy: float, rx: float, ry: float, **kwargs):
        """
        Initialize an ellipse element.
        
        Args:
            cx: X coordinate of the center
            cy: Y coordinate of the center
            rx: X radius of the ellipse
            ry: Y radius of the ellipse
            **kwargs: Additional arguments passed to SVGElement
        """
        super().__init__(**kwargs)
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
    
    def get_points(self, widget_size: Tuple[float, float], 
                  widget_pos: Tuple[float, float], 
                  svg_size: Tuple[float, float]) -> List[float]:
        """
        Get points for the ellipse transformed to widget coordinates.
        
        Args:
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
            
        Returns:
            [center_x, center_y, rx, ry]
        """
        from kivg.path_utils import transform_x, transform_y
        
        w, h = widget_size
        wx, wy = widget_pos
        sw, sh = svg_size
        
        # Transform center coordinates
        center_x = transform_x(self.cx, wx, w, sw, "")
        center_y = transform_y(self.cy, wy, h, sh, "")
        
        # Transform radii
        rx = self.rx * (w / sw)
        ry = self.ry * (h / sh)
        
        return [center_x, center_y, rx, ry]
    
    def render(self, canvas, widget_size: Tuple[float, float], 
              widget_pos: Tuple[float, float], 
              svg_size: Tuple[float, float]) -> None:
        """
        Render the ellipse to a canvas.
        
        Args:
            canvas: Kivy canvas to render to
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
        """
        points = self.get_points(widget_size, widget_pos, svg_size)
        center_x, center_y, rx, ry = points
        
        with canvas:
            # Draw fill if specified
            if self.fill and self.fill[3] > 0:
                Color(*self.fill)
                KivyEllipse(pos=(center_x - rx, center_y - ry), 
                        size=(rx * 2, ry * 2))
            
            # Draw stroke if specified
            if self.stroke and self.stroke[3] > 0:
                Color(*self.stroke)
                KivyLine(ellipse=(center_x - rx, center_y - ry, rx * 2, ry * 2), width=self.stroke_width)


class Path(SVGElement):
    """Path SVG element."""
    
    def __init__(self, d: str, **kwargs):
        """
        Initialize a path element.
        
        Args:
            d: SVG path data string
            **kwargs: Additional arguments passed to SVGElement
        """
        super().__init__(**kwargs)
        self.d = d
        # Parse the path data string into a svg.path object
        from svg.path import parse_path
        self.path = parse_path(d)
    
    def get_points(self, widget_size: Tuple[float, float], 
                  widget_pos: Tuple[float, float], 
                  svg_size: Tuple[float, float]) -> List[List[float]]:
        """
        Get points for the path transformed to widget coordinates.
        
        Args:
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
            
        Returns:
            List of transformed path segments, each containing [type, points]
            where type is "line" or "bezier" and points are the corresponding coordinates
        """
        from kivg.path_utils import line_points, bezier_points
        from svg.path.path import Line, CubicBezier
        
        transformed_segments = []
        
        for segment in self.path:
            if isinstance(segment, Line):
                points = line_points(segment, widget_size, widget_pos, svg_size, "")
                transformed_segments.append(["line", points])
            elif isinstance(segment, CubicBezier):
                points = bezier_points(segment, widget_size, widget_pos, svg_size, "")
                transformed_segments.append(["bezier", points])
        
        return transformed_segments
    
    def render(self, canvas, widget_size: Tuple[float, float], 
              widget_pos: Tuple[float, float], 
              svg_size: Tuple[float, float]) -> None:
        """
        Render the path to a canvas.
        
        Args:
            canvas: Kivy canvas to render to
            widget_size: Size of the widget as (width, height)
            widget_pos: Position of the widget as (x, y)
            svg_size: Size of the SVG as (width, height)
        """
        from kivg.path_utils import get_all_points
        
        segments = self.get_points(widget_size, widget_pos, svg_size)
        
        # For filled paths, we'll use a single Mesh for all segments
        # For stroked paths, we'll use separate Lines for each segment
        
        with canvas:
            # Draw fill if specified
            if self.fill and self.fill[3] > 0:
                Color(*self.fill)
                
                # Collect all points for a complex polygon
                all_points = []
                for segment_type, points in segments:
                    if segment_type == "line":
                        # Line points are [x1, y1, x2, y2]
                        if not all_points:  # Add first point if list is empty
                            all_points.extend(points[:2])
                        all_points.extend(points[2:])  # Add endpoint
                    elif segment_type == "bezier":
                        # Bezier points are [x1, y1, cx1, cy1, cx2, cy2, x2, y2]
                        if not all_points:  # Add first point if list is empty
                            all_points.extend(points[:2])
                        
                        # Generate points along the bezier curve
                        curve_points = get_all_points(
                            (points[0], points[1]),  # start
                            (points[2], points[3]),  # control1
                            (points[4], points[5]),  # control2
                            (points[6], points[7]),  # end
                        )
                        
                        # Skip the first point as it's already in all_points
                        all_points.extend(curve_points[2:])
                
                # Draw the complex polygon using Line strip mode
                # (This is simplified - proper path filling would require triangulation)
                if all_points:
                    KivyLine(points=all_points, close=True, width=1.0)
            
            # Draw stroke if specified
            if self.stroke and self.stroke[3] > 0:
                Color(*self.stroke)
                
                for segment_type, points in segments:
                    if segment_type == "line":
                        # Draw line segment [x1, y1, x2, y2]
                        KivyLine(points=points, width=self.stroke_width)
                    elif segment_type == "bezier":
                        # Draw bezier curve as a series of line segments
                        start = (points[0], points[1])
                        control1 = (points[2], points[3])
                        control2 = (points[4], points[5])
                        end = (points[6], points[7])
                        
                        curve_points = get_all_points(start, control1, control2, end)
                        KivyLine(points=curve_points, width=self.stroke_width)

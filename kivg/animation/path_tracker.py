"""
Path tracking animation for Kivg.
Provides functionality for animating elements along SVG paths.
"""
from typing import List, Tuple, Dict, Any, Callable, Union
import math
from kivy.animation import Animation
from kivy.clock import Clock
from svg.path import parse_path
from svg.path.path import Path, Line, CubicBezier, Arc, QuadraticBezier, Move

from kivg.svg_elements import SVGElement, Circle, Rectangle, Ellipse
from kivg.path_utils import get_all_points, transform_x, transform_y


class PathTracker:
    """
    Handles animation of SVG elements along SVG paths.
    
    This class provides the ability to animate any SVG element 
    (Circle, Rectangle, Ellipse, etc.) along a path defined by 
    SVG path data.
    """
    
    @staticmethod
    def get_point_at_length(path: Path, distance: float) -> Tuple[float, float]:
        """
        Get coordinates of a point at a specific distance along a path.
        
        Args:
            path: SVG path object
            distance: Distance along the path (0.0 to 1.0)
        
        Returns:
            (x, y) coordinates of the point
        """
        if distance <= 0:
            point = path.point(0)
            return point.real, point.imag
        elif distance >= 1:
            point = path.point(1)
            return point.real, point.imag
        
        point = path.point(distance)
        return point.real, point.imag
    
    @staticmethod
    def calculate_rotation(path: Path, distance: float, 
                          step: float = 0.01) -> float:
        """
        Calculate the rotation angle of an element at a specific position on the path.
        
        Args:
            path: SVG path object
            distance: Distance along the path (0.0 to 1.0)
            step: Small step for calculating direction
        
        Returns:
            Rotation angle in degrees
        """
        # Ensure distance is within valid range
        distance = max(0, min(distance, 1))
        
        # For calculation of direction, we need two points
        curr_point = path.point(distance)
        
        # Get next point for direction, handling the end of the path
        next_distance = min(distance + step, 1)
        next_point = path.point(next_distance)
        
        # Calculate direction vector
        dx = next_point.real - curr_point.real
        dy = next_point.imag - curr_point.imag
        
        # Calculate angle
        angle = math.degrees(math.atan2(dy, dx))
        
        return angle
    
    @staticmethod
    def get_path_length(path: Path) -> float:
        """
        Calculate the approximate length of a path.
        
        Args:
            path: SVG path object
        
        Returns:
            Length of the path
        """
        length = 0
        segments = 100  # Number of segments for approximation
        
        for segment in path:
            prev_point = segment.point(0)
            
            for i in range(1, segments + 1):
                t = i / segments
                current_point = segment.point(t)
                
                # Calculate distance between points
                dx = current_point.real - prev_point.real
                dy = current_point.imag - prev_point.imag
                length += math.sqrt(dx * dx + dy * dy)
                
                prev_point = current_point
        
        return length
    
    @staticmethod
    def animate_element_along_path(
        element: SVGElement,
        path_data: str,
        widget: Any,
        svg_size: List[float],
        duration: float = 2.0,
        repeat: bool = False,
        rotate: bool = False,
        callback: Callable = None,
        other_elements: List[SVGElement] = None,
        show_path: bool = True
    ) -> Animation:
        """
        Animate an SVG element along a path.
        
        Args:
            element: SVG element to animate
            path_data: SVG path data string
            widget: Kivy widget to render on
            svg_size: SVG dimensions [width, height]
            duration: Animation duration in seconds
            repeat: Whether to repeat the animation
            rotate: Whether to rotate the element to follow the path direction
            callback: Function to call on animation completion
            other_elements: Other SVG elements to render alongside the animated element
            show_path: Whether to show the full path during animation
        
        Returns:
            Kivy Animation object
        """
        print(f"Starting animation with element: {element}")
        print(f"Path data: {path_data}")
        print(f"SVG size: {svg_size}")
        print(f"Repeat: {repeat}")
        
        # Parse the path data
        try:
            path = parse_path(path_data)
        except Exception as e:
            print(f"Error parsing path data: {e}")
            return None
        
        # Create a property to track animation progress
        widget.path_progress = 0
        
        # Store original element properties for animation
        original_props = {}
        
        # Store the path visualization element if needed
        path_element = None
        if show_path:
            # Import here to avoid circular imports
            from kivg.svg_elements import Path as SVGPath
            path_element = SVGPath(
                d=path_data,
                element_id="animation_path",
                fill=[0, 0, 0, 0],  # Transparent fill
                stroke=[0.7, 0.7, 0.7, 0.5],  # Light gray with transparency
                stroke_width=1.0
            )
            
        # Create a tracking line to show the progress along the path
        tracking_points = []
        
        # Function to update element position during animation
        def update_element_position(progress):
            # Get point at current distance along the path
            x, y = PathTracker.get_point_at_length(path, progress)
            
            # Keep track of the path traveled so far
            tracking_points.append((x, y))
            if len(tracking_points) > 1000:  # Limit the number of tracking points
                tracking_points.pop(0)
            
            # Update element position based on type
            if isinstance(element, Circle) or isinstance(element, Ellipse):
                # Circle or Ellipse
                if not original_props:
                    original_props['cx'] = element.cx
                    original_props['cy'] = element.cy
                
                # Update position
                element.cx = x
                element.cy = y
                
                # Apply rotation if requested
                if rotate:
                    angle = PathTracker.calculate_rotation(path, progress)
                    # Save rotation if needed
                    if not hasattr(element, '_rotation'):
                        element._rotation = 0
                    element._rotation = angle
            
            elif isinstance(element, Rectangle):
                # Rectangle
                if not original_props:
                    original_props['x'] = element.x
                    original_props['y'] = element.y
                    
                # Center the rectangle on the path point
                element.x = x - element.width / 2
                element.y = y - element.height / 2
                
                # Apply rotation if requested
                if rotate:
                    angle = PathTracker.calculate_rotation(path, progress)
                    if not hasattr(element, '_rotation'):
                        element._rotation = 0
                    element._rotation = angle
            
            # Redraw the widget with the updated element
            widget.canvas.clear()
            
            # Draw the full path if requested
            if show_path and path_element:
                path_element.render(widget.canvas, widget.size, widget.pos, svg_size)
                
            # Draw other elements in the background
            if other_elements:
                for elem in other_elements:
                    if elem != element:  # Don't draw the animated element twice
                        elem.render(widget.canvas, widget.size, widget.pos, svg_size)
            
            # Draw the animated element on top
            element.render(widget.canvas, widget.size, widget.pos, svg_size)
        
        # Create animation
        animation = Animation(path_progress=1.0, duration=duration)
        
        # Bind update function
        def on_progress(animation, widget, value):
            update_element_position(widget.path_progress)
        
        animation.bind(on_progress=on_progress)
        
        # Handle repeat
        if repeat:
            # We need to implement our own repeat logic
            def repeat_animation(*args):
                # Reset progress to 0
                widget.path_progress = 0
                # And start the animation again
                animation.start(widget)
                
            # Bind to animation complete to restart
            animation.bind(on_complete=repeat_animation)
        else:
            # Handle normal completion
            def on_complete(animation, widget):
                if callback:
                    callback()
                
                # Restore original properties if not repeating
                if original_props:
                    for key, value in original_props.items():
                        setattr(element, key, value)
                    widget.canvas.clear()
                    
                    # Redraw all elements in their original positions
                    if show_path and path_element:
                        path_element.render(widget.canvas, widget.size, widget.pos, svg_size)
                        
                    if other_elements:
                        for elem in other_elements:
                            elem.render(widget.canvas, widget.size, widget.pos, svg_size)
                    else:
                        element.render(widget.canvas, widget.size, widget.pos, svg_size)
            
            animation.bind(on_complete=on_complete)
        
        # Start the animation
        animation.start(widget)
        
        return animation


# Add element-specific convenience methods that can be used directly from SVG elements

def add_path_tracking_to_elements():
    """Add path tracking methods to all SVG element classes."""
    from kivg.svg_elements import SVGElement, Path
    
    def animate_along_path(
        self,
        path: Union[str, 'Path'],
        widget: Any,
        svg_size: List[float],
        duration: float = 2.0,
        repeat: bool = False,
        rotate: bool = False,
        callback: Callable = None
    ) -> Animation:
        """
        Animate this element along a path.
        
        Args:
            path: Path object or path data string
            widget: Kivy widget to render on
            svg_size: SVG dimensions [width, height]
            duration: Animation duration in seconds
            repeat: Whether to repeat the animation
            rotate: Whether to rotate the element to follow path direction
            callback: Function to call on animation completion
            
        Returns:
            Kivy Animation object
        """
        # Convert Path object to path data string if needed
        path_data = path.d if isinstance(path, Path) else path
        
        return PathTracker.animate_element_along_path(
            self, path_data, widget, svg_size, duration, repeat, rotate, callback
        )
    
    # Add the method to the base class so all elements inherit it
    SVGElement.animate_along_path = animate_along_path


# Add the methods to element classes when this module is imported
add_path_tracking_to_elements()
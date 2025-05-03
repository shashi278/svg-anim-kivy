"""
Kivg - SVG drawing and animation for Kivy
Core class and main API
"""

from collections import OrderedDict
from typing import List, Tuple, Dict, Any, Callable

from kivg.animation.kivy_animation import Animation
from kivg.drawing.manager import DrawingManager
from kivg.animation.handler import AnimationHandler
from kivg.mesh_handler import MeshHandler
from kivg.svg_elements import SVGElement
from kivg.svg_renderer import SvgRenderer


class Kivg:
    """
    Main class for rendering and animating SVG files in Kivy applications.
    
    This class provides methods to draw SVG files onto Kivy widgets and
    animate them using various techniques.
    """

    def __init__(self, widget: Any, *args):
        """
        Initialize the Kivg renderer.
        
        Args:
            widget: Kivy widget to draw SVG upon
            *args: Additional arguments (not currently used)
        """
        self.widget = widget  # Target widget for rendering
        self._fill = True  # Fill path with color after drawing
        self._line_width = 2
        self._line_color = [0, 0, 0, 1]
        self._animation_duration = 0.02
        self._previous_svg_file = ""  # Cache previous SVG file
        
        # Animation state
        self.path = []
        self.closed_shapes = OrderedDict()
        self.svg_size = []
        self.current_svg_file = ""
        
        # Shape animation state
        self.all_anim = []
        self.curr_count = 0
        self.prev_shapes = []
        self.curr_shape = []

    def fill_up(self, shapes: List[List[float]], color: List[float]) -> None:
        """
        Fill shapes with specified color using mesh rendering.
        
        Args:
            shapes: List of shape point lists to fill
            color: RGB or RGBA color to fill with
        """
        print("shapes", shapes)
        MeshHandler.render_mesh(self.widget, shapes, color, "mesh_opacity")

    def fill_up_shapes(self, *args) -> None:
        """Fill all shapes in the current SVG file."""
        for id_, closed_paths in self.closed_shapes.items():
            color = self.closed_shapes[id_]["color"]
            print("calling fill_up")
            self.fill_up(closed_paths[id_ + "shapes"], color)
    
    def fill_up_shapes_anim(self, shapes: List[Tuple[List[float], List[float]]], *args) -> None:
        """Fill shapes during animation."""
        for shape in shapes:
            color = shape[0]
            self.fill_up([shape[1]], color)
    
    def anim_on_comp(self, *args) -> None:
        """Handle completion of an animation in the sequence."""
        self.curr_count += 1
        self.prev_shapes.append(self.curr_shape)
        
        if self.curr_count < len(self.all_anim):
            id_, animation = self.all_anim[self.curr_count]
            setattr(self, "curr_id", id_)
            setattr(self, "curr_clr", self.closed_shapes[id_]["color"])
            
            # Clear previous bindings and add new ones
            animation.unbind(on_progress=self.track_progress)
            animation.unbind(on_complete=self.anim_on_comp)
            
            animation.bind(on_progress=self.track_progress)
            animation.bind(on_complete=self.anim_on_comp)
            
            animation.start(self.widget)
    
    def track_progress(self, *args) -> None:
        """
        Track animation progress and update the canvas.
        
        Called during animation progress. Updates the current shape.
        """
        id_ = getattr(self, "curr_id")
        elements_list = getattr(self, f"{id_}_tmp")

        shape_list = SvgRenderer.collect_shape_points(elements_list, self.widget, id_)
        
        self.widget.canvas.clear()
        self.curr_shape = (getattr(self, "curr_clr"), shape_list)
        shapes = [*self.prev_shapes, self.curr_shape]
        self.fill_up_shapes_anim(shapes)

    def update_canvas(self, *args, **kwargs) -> None:
        """Update the canvas with the current drawing state."""
        SvgRenderer.update_canvas(self.widget, self.path, self._line_color)

    def draw(self, svg_file: str, animate: bool = False, 
             anim_type: str = "seq", *args, **kwargs) -> None:
        """
        Draw an SVG file onto the widget with optional animation.
        
        Args:
            svg_file: Path to the SVG file
            animate: Whether to animate the drawing process
            anim_type: Animation type - "seq" for sequential or "par" for parallel
            
        Keyword Args:
            fill: Whether to fill the drawing (bool)
            line_width: Width of lines (int)
            line_color: Color of lines (list)
            dur: Duration of each animation step (float)
            from_shape_anim: Whether called from shape_animate (bool)
        """
        # Process arguments
        fill = kwargs.get("fill", self._fill)
        line_width = kwargs.get("line_width", self._line_width)
        line_color = kwargs.get("line_color", self._line_color)
        duration = kwargs.get("dur", self._animation_duration)
        from_shape_anim = kwargs.get("from_shape_anim", False)
        anim_type = anim_type if anim_type in ("seq", "par") else "seq"
        
        # Set current values as instance attributes for other methods to access
        self._fill = fill
        self._line_width = line_width
        self._line_color = line_color
        self._animation_duration = duration
        self.current_svg_file = svg_file
        
        # Only process SVG if it's different from the previous one
        if svg_file != self._previous_svg_file:
            self.svg_size, self.closed_shapes, self.path = DrawingManager.process_path_data(svg_file)
            print(f"SVG size: {self.svg_size}")
            print(f"Closed shapes: {self.closed_shapes}")
            print(f"Path data: {self.path}")
            self._previous_svg_file = svg_file
        
        # Calculate the paths and get animation list
        anim_list = DrawingManager.calculate_paths(
            self.widget, self.closed_shapes, self.svg_size, 
            svg_file, animate, line_width, duration
        )
        
        # Handle animation and rendering
        if not from_shape_anim:
            if animate:
                # Combine animations according to anim_type
                anim = AnimationHandler.create_animation_sequence(
                    anim_list, sequential=(anim_type == "seq")
                )
                
                # Add fill animation if needed
                if fill:
                    setattr(self.widget, "mesh_opacity", 0)
                    anim = AnimationHandler.add_fill_animation(
                        anim, self.widget, self.fill_up_shapes
                    )
                
                # Start the animation
                AnimationHandler.prepare_and_start_animation(
                    anim, self.widget, self.update_canvas
                )
            else:
                # Static rendering
                Animation.cancel_all(self.widget)
                # for element in svg_elements:
                #     print("Rendering element:", element)
                #     canvas = self.widget.canvas
                #     canvas.clear()
                #     element.render(canvas, self.widget.size, 
                #                    self.widget.pos, self.svg_size)
                # if not fill:
                self.update_canvas()
                # else:
                    # self.widget.canvas.clear()
                    # self.fill_up_shapes()

    def shape_animate(self, svg_file: str, anim_config_list: List[Dict] = None, 
                     on_complete: Callable = None) -> None:
        """
        Animate individual shapes in an SVG file.
        
        Args:
            svg_file: Path to the SVG file
            anim_config_list: List of animation configurations, each containing:
                - id_: Shape ID to animate
                - from_: Direction of animation
                - d: Duration (optional)
                - t: Transition (optional)
            on_complete: Function to call when all animations complete
        """
        if anim_config_list is None:
            anim_config_list = []
            
        # First draw the SVG without animation
        self.draw(svg_file, from_shape_anim=True)
        setattr(self.widget, "mesh_opacity", 1)

        # Initialize animation state
        self.all_anim = []
        self.curr_count = 0
        self.prev_shapes = []
        self.curr_shape = []
        
        # Prepare animations using AnimationHandler
        self.all_anim = AnimationHandler.prepare_shape_animations(
            self,
            self.widget,
            anim_config_list,
            self.closed_shapes,
            self.svg_size,
            self.current_svg_file
        )
        
        # Start animations if any are ready
        if self.all_anim:
            id_, animation = self.all_anim[0]
            setattr(self, "curr_id", id_)
            setattr(self, "curr_clr", self.closed_shapes[id_]["color"])
            
            # Attach progress tracking
            animation.bind(on_progress=self.track_progress)
            
            # Attach completion callback if provided
            if on_complete and self.all_anim:
                self.all_anim[-1][1].bind(on_complete=on_complete)
            
            # Start the animation
            animation.cancel_all(self.widget)
            animation.bind(on_complete=self.anim_on_comp)
            animation.start(self.widget)
        elif anim_config_list:
            # In case there are config items but no animations were created
            if on_complete:
                on_complete()
                
    def animate_element_along_path(self, element_id: str, path_id: str, duration: float = 2.0, 
                                  repeat: bool = False, rotate: bool = False,
                                  callback: Callable = None, keep_others: bool = True,
                                  show_path: bool = True) -> None:
        """
        Animate an SVG element along a path.
        
        This method allows any SVG element (Circle, Rectangle, Ellipse, etc.) to be 
        animated along a path defined in the current SVG file.
        
        Args:
            element_id: ID of the element to animate
            path_id: ID of the path to follow
            duration: Animation duration in seconds
            repeat: Whether to repeat the animation
            rotate: Whether to rotate the element to follow the path direction
            callback: Function to call when animation completes
            keep_others: Whether to keep rendering other elements during animation
            show_path: Whether to show the full path during animation
        """
        # Import here to avoid circular imports
        from kivg.animation.path_tracker import PathTracker
        
        # Ensure we have an SVG loaded
        if not self.current_svg_file or not self.closed_shapes:
            print("No SVG file loaded. Call draw() first.")
            return None
        
        # Use the closed_shapes dictionary directly to find elements
        element = None
        path_data = None
        
        # Find the element by ID
        if element_id in self.closed_shapes and 'element' in self.closed_shapes[element_id]:
            element = self.closed_shapes[element_id]['element']
        else:
            print(f"Element with ID '{element_id}' not found in SVG.")
            return None
        
        # Find the path by ID
        if path_id in self.closed_shapes:
            # Check if it's a Path element
            if hasattr(self.closed_shapes[path_id]['element'], 'd'):
                path_data = self.closed_shapes[path_id]['element'].d
            # Otherwise try to get the 'd' attribute directly
            elif 'd' in self.closed_shapes[path_id]:
                path_data = self.closed_shapes[path_id]['d']
        
        if not path_data:
            print(f"Path with ID '{path_id}' not found in SVG or is not a path element.")
            return None
        
        print(f"Animating {element_id} along path {path_id}")
        print(f"Element: {element}")
        print(f"Path data: {path_data}")
        
        # Get all other elements to render during animation
        other_elements = []
        if keep_others:
            for id_, data in self.closed_shapes.items():
                if id_ != element_id and 'element' in data:
                    other_elements.append(data['element'])
        
        # Clear the canvas for animation
        self.widget.canvas.clear()
        
        # Start the animation
        return PathTracker.animate_element_along_path(
            element, path_data, self.widget, self.svg_size, 
            duration, repeat, rotate, callback, 
            other_elements if keep_others else None,
            show_path
        )

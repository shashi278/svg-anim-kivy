"""
ShapeAnimationManager handles the coordination between animation management and shape-specific animations.
"""

from typing import List, Dict, Tuple, Any, Optional, Callable

from kivg.data_classes import AnimationContext
from kivg.shape_animation import ShapeAnimator
from kivg.animation_handler import AnimationHandler
from .animation import Animation


class ShapeAnimationManager:
    """
    Coordinates between the AnimationHandler and ShapeAnimator to manage shape animations.
    
    This class serves as a bridge to make all animations work through a common system,
    while preserving the specialized shape animation logic.
    """
    
    @staticmethod
    def prepare_shape_animations(
        caller: Any,
        widget: Any,
        anim_config_list: List[Dict],
        closed_shapes: Dict,
        svg_size: List[float],
        svg_file: str
    ) -> List[Tuple[str, Animation]]:
        """
        Prepare animations for shapes based on configuration.
        
        Args:
            caller: Object calling the animation (typically Kivg instance)
            widget: Widget to animate
            anim_config_list: List of animation configuration dictionaries
            closed_shapes: SVG path data organized by shape ID
            svg_size: SVG dimensions
            svg_file: SVG file path
            
        Returns:
            List of tuples (shape_id, animation) for the shapes
        """
        animation_list = []
        
        for config in anim_config_list:
            # Create animation context
            context = AnimationContext(
                widget=widget,
                shape_id=config["id_"],
                direction=config.get("from_", None),
                transition=config.get("t", "out_sine"),
                duration=config.get("d", 0.3),
                closed_shapes=closed_shapes,
                sw_size=svg_size,
                svg_file=svg_file
            )
            
            # Get animation list from ShapeAnimator
            anim_list = ShapeAnimator.setup_animation(caller, context)
            
            if anim_list:
                # Combine animations in parallel
                combined_anim = AnimationHandler.create_animation_sequence(
                    anim_list, sequential=False
                )
                animation_list.append((config["id_"], combined_anim))
                
        return animation_list
    
    @staticmethod
    def start_shape_animations(
        animations: List[Tuple[str, Animation]],
        widget: Any,
        on_progress_callback: Callable,
        on_complete_callback: Optional[Callable] = None
    ) -> None:
        """
        Start shape animations in sequence.
        
        Args:
            animations: List of (shape_id, animation) tuples
            widget: Widget to animate
            on_progress_callback: Callback for animation progress
            on_complete_callback: Optional callback for animation completion
        """
        if not animations:
            return
            
        # Set up the first animation
        id_, animation = animations[0]
        
        # Cancel any running animations
        animation.cancel_all(widget)
        
        # Bind callbacks
        animation.bind(on_progress=on_progress_callback)
        
        # Bind completion callback to the last animation if provided
        if on_complete_callback and len(animations) > 0:
            animations[-1][1].bind(on_complete=on_complete_callback)
        
        # Start the animation
        animation.start(widget)
    
    @staticmethod
    def create_shape_animation(
        shape_id: str,
        direction: str,
        widget: Any,
        closed_shapes: Dict,
        svg_size: List[float],
        svg_file: str,
        transition: str = "out_sine",
        duration: float = 0.3
    ) -> Optional[Animation]:
        """
        Create an animation for a single shape.
        
        Args:
            shape_id: ID of the shape to animate
            direction: Direction of animation (left, right, top, bottom, etc.)
            widget: Widget to animate
            closed_shapes: SVG path data organized by shape ID
            svg_size: SVG dimensions
            svg_file: SVG file path
            transition: Animation transition type
            duration: Animation duration in seconds
            
        Returns:
            Animation object or None if shape not found
        """
        context = AnimationContext(
            widget=widget,
            shape_id=shape_id,
            direction=direction,
            transition=transition,
            duration=duration,
            closed_shapes=closed_shapes,
            sw_size=svg_size,
            svg_file=svg_file
        )
        
        # Use a temporary caller object since we don't need to store state
        caller = type('TempCaller', (), {'prev_shapes': [], 'curr_shape': []})()
        
        anim_list = ShapeAnimator.setup_animation(caller, context)
        
        if anim_list:
            return AnimationHandler.create_animation_sequence(
                anim_list, sequential=False
            )
        
        return None
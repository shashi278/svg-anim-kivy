"""
AnimationHandler manages animation creation and sequencing.
"""

from typing import List, Any, Optional, Callable

from .kivy_animation import Animation
from ..data_classes import AnimationContext
from .animation_shapes import ShapeAnimator


class AnimationHandler:
    """Centralized handler for all types of animations in Kivg."""
    
    @staticmethod
    def create_animation_sequence(animations: List[Animation], 
                                 sequential: bool = True) -> Optional[Animation]:
        """
        Create a sequence or parallel animation from multiple animations.
        
        Args:
            animations: List of Animation objects
            sequential: If True, animations run in sequence, otherwise in parallel
            
        Returns:
            Combined Animation object or None if animations list is empty
        """
        if not animations:
            return None
            
        combined = animations[0]
        for anim in animations[1:]:
            if sequential:
                combined += anim  # Sequential
            else:
                combined &= anim  # Parallel
                
        return combined
    
    @staticmethod
    def add_fill_animation(anim: Animation, widget: Any, 
                          on_progress_callback=None) -> Animation:
        """
        Add a fade-in animation for shape filling.
        
        Args:
            anim: Base animation to add fill animation to
            widget: Widget to animate
            on_progress_callback: Callback for animation progress
            
        Returns:
            Animation with fill effect added
        """
        fill_anim = Animation(d=0.4, mesh_opacity=1)
        
        if on_progress_callback:
            fill_anim.bind(on_progress=on_progress_callback)
            
        return anim + fill_anim
    
    @staticmethod
    def prepare_and_start_animation(
        anim: Animation, 
        widget: Any, 
        on_progress_callback: Optional[Callable] = None,
        on_complete_callback: Optional[Callable] = None
    ) -> None:
        """
        Prepare and start an animation.
        
        Args:
            anim: Animation to start
            widget: Widget to animate
            on_progress_callback: Callback for animation progress
            on_complete_callback: Callback for animation completion
        """
        anim.cancel_all(widget)
        
        if on_progress_callback:
            anim.bind(on_progress=on_progress_callback)
            
        if on_complete_callback:
            anim.bind(on_complete=on_complete_callback)
            
        anim.start(widget)
    
    @staticmethod
    def setup_shape_animations(
        caller: Any,
        context: AnimationContext
    ) -> List[Animation]:
        """
        Set up animations for a shape using ShapeAnimator.
        
        Args:
            caller: The caller object (usually Kivg instance)
            context: AnimationContext with animation parameters
            
        Returns:
            List of Animation objects
        """
        return ShapeAnimator.setup_animation(caller, context)
        
    @staticmethod
    def prepare_shape_animations(
        caller: Any,
        widget: Any,
        anim_config_list: List[dict],
        closed_shapes: dict,
        svg_size: List[float],
        svg_file: str
    ) -> List[tuple]:
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
            anim_list = AnimationHandler.setup_shape_animations(caller, context)
            
            if anim_list:
                # Combine animations in parallel
                combined_anim = AnimationHandler.create_animation_sequence(
                    anim_list, sequential=False
                )
                animation_list.append((config["id_"], combined_anim))
                
        return animation_list

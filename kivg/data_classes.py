from dataclasses import dataclass

@dataclass
class AnimationContext:
    widget: object
    shape_id: str
    direction: str
    transition: str
    duration: float
    closed_shapes: dict
    sw_size: tuple
    svg_file: str

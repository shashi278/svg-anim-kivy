"""
SVG parsing utilities for Kivg.
Handles parsing SVG files and extracting path data.
"""
from typing import Tuple, List, Dict, Any
from xml.dom import minidom
from kivy.utils import get_color_from_hex

def parse_svg(svg_file: str) -> Tuple[List[float], List[Tuple[str, str, List[float]]]]:
    """
    Parse an SVG file and extract relevant information.
    
    Args:
        svg_file: Path to the SVG file
        
    Returns:
        Tuple containing (svg_dimensions, path_data)
            - svg_dimensions: [width, height]
            - path_data: List of tuples (path_string, element_id, color)
    """
    try:
        doc = minidom.parse(svg_file)
    except Exception as e:
        raise ValueError(f"Failed to parse SVG file '{svg_file}': {e}")

    # Extract viewBox
    svg_element = doc.getElementsByTagName("svg")[0]
    viewbox_string = svg_element.getAttribute("viewBox")
    
    # Parse viewBox dimensions
    if "," in viewbox_string:
        sw_size = list(map(float, viewbox_string.split(",")[2:]))
    else:
        sw_size = list(map(float, viewbox_string.split(" ")[2:]))

    # Extract path data
    path_count = 0
    path_strings = []
    for path in doc.getElementsByTagName("path"):
        id_ = path.getAttribute("id") or f"path_{path_count}"
        d = path.getAttribute("d")
        try:
            fill_attr = path.getAttribute("fill")
            clr = get_color_from_hex(fill_attr) if fill_attr else [1, 1, 1, 0]
        except ValueError:
            clr = [1, 1, 1, 0]  # Default if color format is different
        
        path_strings.append((d, id_, clr))
        path_count += 1
    
    doc.unlink()
    return sw_size, path_strings

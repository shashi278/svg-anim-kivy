"""
SVG parsing utilities for Kivg.
Handles parsing SVG files and extracting path data.
"""
from typing import Tuple, List, Dict, Any, Union
from xml.dom import minidom
from kivy.utils import get_color_from_hex
from svg.path import parse_path
from svg.path.path import Line, CubicBezier

# Import SVG element classes
from kivg.svg_elements import Circle as SVGCircle
from kivg.svg_elements import Rectangle as SVGRectangle
from kivg.svg_elements import Ellipse as SVGEllipse
from kivg.svg_elements import SVGElement


def parse_color(color_attr: str) -> List[float]:
    """
    Parse an SVG color attribute to RGBA.
    
    Args:
        color_attr: SVG color attribute
        
    Returns:
        RGBA color as [r, g, b, a]
    """
    if not color_attr or color_attr == "none":
        return [0, 0, 0, 0]
    
    try:
        if color_attr.startswith("#"):
            return get_color_from_hex(color_attr)
        elif color_attr == "transparent":
            return [0, 0, 0, 0]
        elif color_attr.startswith("rgb"):
            # Parse rgb(r, g, b) or rgba(r, g, b, a)
            values = color_attr.strip().replace("rgb", "").replace("a", "").strip("()").split(",")
            if len(values) >= 3:
                r = float(values[0].strip()) / 255
                g = float(values[1].strip()) / 255
                b = float(values[2].strip()) / 255
                a = float(values[3].strip()) if len(values) >= 4 else 1.0
                return [r, g, b, a]
    except Exception:
        pass
    
    # Default to black with full opacity
    return [0, 0, 0, 1]


def parse_svg(svg_file: str) -> Tuple[List[float], Dict[str, Any]]:
    """
    Parse an SVG file and extract relevant information.
    
    Args:
        svg_file: Path to the SVG file
        
    Returns:
        Tuple containing (svg_dimensions, elements_data)
            - svg_dimensions: [width, height]
            - elements_data: Dictionary of SVG elements by ID
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

    # Store all SVG elements
    elements_data = {}
    
    # Extract path data
    path_count = 0
    for path in doc.getElementsByTagName("path"):
        id_ = path.getAttribute("id") or f"path_{path_count}"
        d = path.getAttribute("d")
        
        # Parse fill and stroke
        fill = parse_color(path.getAttribute("fill"))
        stroke = parse_color(path.getAttribute("stroke"))
        stroke_width = float(path.getAttribute("stroke-width") or 1.0)
        
        # Create path element
        from kivg.svg_elements import Path as SVGPath
        path_element = SVGPath(
            d=d,
            element_id=id_,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width
        )
        
        # Store path data
        elements_data[id_] = {
            "element": path_element,
            "type": "path"
        }
        
        path_count += 1
    
    # Extract circle elements
    circle_count = 0
    for circle in doc.getElementsByTagName("circle"):
        id_ = circle.getAttribute("id") or f"circle_{circle_count}"
        cx = float(circle.getAttribute("cx") or 0)
        cy = float(circle.getAttribute("cy") or 0)
        r = float(circle.getAttribute("r") or 0)
        
        # Parse fill and stroke
        fill = parse_color(circle.getAttribute("fill"))
        stroke = parse_color(circle.getAttribute("stroke"))
        stroke_width = float(circle.getAttribute("stroke-width") or 1.0)
        
        # Create circle element
        circle_element = SVGCircle(
            cx=cx, cy=cy, r=r,
            element_id=id_,
            fill=fill, 
            stroke=stroke, 
            stroke_width=stroke_width
        )
        
        # Store circle data
        elements_data[id_] = {
            "element": circle_element,
            "type": "circle"
        }
        
        circle_count += 1
    
    # Extract rectangle elements
    rect_count = 0
    for rect in doc.getElementsByTagName("rect"):
        id_ = rect.getAttribute("id") or f"rect_{rect_count}"
        x = float(rect.getAttribute("x") or 0)
        y = float(rect.getAttribute("y") or 0)
        width = float(rect.getAttribute("width") or 0)
        height = float(rect.getAttribute("height") or 0)
        rx = float(rect.getAttribute("rx") or 0)
        ry = float(rect.getAttribute("ry") or 0)
        
        # Parse fill and stroke
        fill = parse_color(rect.getAttribute("fill"))
        stroke = parse_color(rect.getAttribute("stroke"))
        stroke_width = float(rect.getAttribute("stroke-width") or 1.0)
        
        # Create rectangle element
        rect_element = SVGRectangle(
            x=x, y=y, width=width, height=height, rx=rx, ry=ry,
            element_id=id_,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width
        )
        
        # Store rectangle data
        elements_data[id_] = {
            "element": rect_element,
            "type": "rect"
        }
        
        rect_count += 1
    
    # Extract ellipse elements
    ellipse_count = 0
    for ellipse in doc.getElementsByTagName("ellipse"):
        id_ = ellipse.getAttribute("id") or f"ellipse_{ellipse_count}"
        cx = float(ellipse.getAttribute("cx") or 0)
        cy = float(ellipse.getAttribute("cy") or 0)
        rx = float(ellipse.getAttribute("rx") or 0)
        ry = float(ellipse.getAttribute("ry") or 0)
        
        # Parse fill and stroke
        fill = parse_color(ellipse.getAttribute("fill"))
        stroke = parse_color(ellipse.getAttribute("stroke"))
        stroke_width = float(ellipse.getAttribute("stroke-width") or 1.0)
        
        # Create ellipse element
        ellipse_element = SVGEllipse(
            cx=cx, cy=cy, rx=rx, ry=ry,
            element_id=id_,
            fill=fill, 
            stroke=stroke, 
            stroke_width=stroke_width
        )
        
        # Store ellipse data
        elements_data[id_] = {
            "element": ellipse_element,
            "type": "ellipse"
        }
        
        ellipse_count += 1
    
    # Note: Arc handling has been removed
    
    doc.unlink()
    return sw_size, elements_data


def get_svg_elements(elements_data: Dict[str, Any]) -> List[SVGElement]:
    """
    Extract SVG elements from parsed data.
    
    Args:
        elements_data: Dictionary of SVG elements data from parse_svg
        
    Returns:
        List of SVGElement objects
    """
    elements = []
    
    for id_, data in elements_data.items():
        if "element" in data:
            elements.append(data["element"])
    
    return elements

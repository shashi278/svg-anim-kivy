
from svg.path.path import Line, CubicBezier
from xml.dom import minidom
from kivy.utils import get_color_from_hex as gch

# working with ratio to get a given svg path coordinate wrt to given widget
"""
x_pos, y_pos: svg path coordinate
wx, wy: widget pos
w, h: widget size
sw, sh: svg size
sf: svg_file, only needed for kivy icon support
"""
# Special support for Kivy svg Icon :)
x = lambda x_pos, wx, w, sw, sf: wx + (
    w * (x_pos / 10) / sw if "kivy" in sf else w * x_pos / sw
)
y = lambda y_pos, wy, h, sh, sf: wy + (
    h * ((y_pos / 10)) / sh if "kivy" in sf else h * (sh - y_pos) / sh
)


def point(complex_point: complex, w, h, wx, wy, sw, sh, sf):
    return [x(complex_point.real, wx, w, sw, sf), y(complex_point.imag, wy, h, sh, sf)]


def bezier_points(e: CubicBezier, w, h, wx, wy, sw, sh, sf):
    return [
        *point(e.start, w, h, wx, wy, sw, sh, sf),
        *point(e.control1, w, h, wx, wy, sw, sh, sf),
        *point(e.control2, w, h, wx, wy, sw, sh, sf),
        *point(e.end, w, h, wx, wy, sw, sh, sf),
    ]


def line_points(e: Line, w, h, wx, wy, sw, sh, sf):
    return [
        *point(e.start, w, h, wx, wy, sw, sh, sf),
        *point(e.end, w, h, wx, wy, sw, sh, sf),
    ]


# https://stackoverflow.com/a/15399173/8871954
B0_t = lambda t: (1 - t) ** 3
B1_t = lambda t: 3 * t * (1 - t) ** 2
B2_t = lambda t: 3 * t ** 2 * (1 - t)
B3_t = lambda t: t ** 3


def get_all_points(start, c1, c2, end):
    points = []
    ax, ay = start
    dx, dy = end
    bx, by = c1
    cx, cy = c2

    seg = 1 / 40
    t = 0

    while t <= 1:
        points.extend(
            [
                (B0_t(t) * ax) + (B1_t(t) * bx) + (B2_t(t) * cx) + (B3_t(t) * dx),
                (B0_t(t) * ay) + (B1_t(t) * by) + (B2_t(t) * cy) + (B3_t(t) * dy),
            ]
        )
        t += seg

    return points

def parse_svg(svg_file):
    doc = minidom.parse(svg_file)

    viewbox_string = doc.getElementsByTagName("svg")[0].getAttribute("viewBox")
    sw_size = list(
        map(
            int,
            viewbox_string.split(",")[2:]
            if "," in viewbox_string
            else viewbox_string.split(" ")[2:],
        )
    )

    path_count = 0
    path_strings = []
    for path in doc.getElementsByTagName("path"):
        id_ = path.getAttribute("id") or "path_{}".format(path_count)
        d = path.getAttribute("d")
        try:
            clr = gch(path.getAttribute("fill")) or [1, 1, 1, 0]
        except ValueError:
            clr = [1, 1, 1, 0]  # if color format is different
        path_strings.append((d, id_, clr))
        path_count += 1
    doc.unlink()

    return sw_size, path_strings

def find_center(input_list):
    middle = float(len(input_list))/2
    if middle % 2 != 0: return input_list[int(middle - .5)]
    else: return (input_list[int(middle)]+input_list[int(middle-1)])/2

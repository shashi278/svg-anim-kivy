from kivy.graphics import (
    Line as KivyLine,
    Bezier as KivyBezier,
    Color,
    Rectangle,
    Ellipse,
    Triangle,
    Mesh,
)
from kivy.graphics.tesselator import Tesselator, WINDING_ODD, TYPE_POLYGONS
from kivy.animation import Animation
from kivy.utils import get_color_from_hex as gch
from kivy.properties import NumericProperty

from svg.path import parse_path
from svg.path.path import Line, CubicBezier, Close, Move
from xml.dom import minidom

from collections import OrderedDict


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


class SVGAnimation:
    def __init__(self, widget, *args):
        """
        widget: widget to draw svg upon
        """
        self.b = widget
        self._fill = True  # Fill path with color after drawing
        self._LINE_WIDTH = 2
        self._LINE_COLOR = [0, 0, 0, 1]
        self._DUR = 0.02
        self.psf = ""  # Previous svg file - Don't re-find path for same file in a row

    def get_tess(self, shapes):
        tess = Tesselator()
        for shape in shapes:
            if len(shape) >= 3:
                tess.add_contour(shape)
        return tess

    def get_mesh(self, shapes):
        tess = self.get_tess(shapes)
        ret = tess.tesselate(WINDING_ODD, TYPE_POLYGONS)
        return tess.meshes

    def fill_up(self, shapes, color):
        meshes = self.get_mesh(shapes)
        with self.b.canvas:
            Color(*color[:3], self.b.mesh_opacity)
            for vertices, indices in meshes:
                Mesh(vertices=vertices, indices=indices, mode="triangle_fan")

    def fill_up_shapes(self, *args):
        for id_, closed_paths in self.closed_shapes.items():
            c = self.closed_shapes[id_]["color"]
            self.fill_up(closed_paths[id_ + "shapes"], c)

    def draw(self, svg_file, animate=False, *args, **kwargs):
        """
        Function to animate
        
        Call this function with an svg file name to animate that svg
        
        ------------
        Extra arguments:
        
        fill: Whether to fill the drawing at the end using same png, defaults true,
         unexpected result if png with same name is not available
        
        line_width: Line width for drawing, default 2
        
        line_color: Line Color for drawing, default [0,0,0,1]
        
        dur: Duration of each small path drawing animation, default .02
        """
        self.fill = kwargs.get("fill", self._fill)
        self.LINE_WIDTH = kwargs.get("line_width", self._LINE_WIDTH)
        self.LINE_COLOR = kwargs.get("line_color", self._LINE_COLOR)
        self.DUR = kwargs.get("dur", self._DUR)

        self.sf = svg_file
        if self.sf != self.psf:
            doc = minidom.parse(svg_file)

            viewbox_string = doc.getElementsByTagName("svg")[0].getAttribute("viewBox")
            self.sw_size = list(
                map(
                    int,
                    viewbox_string.split(",")[2:]
                    if "," in viewbox_string
                    else viewbox_string.split(" ")[2:],
                )
            )

            path_count = 0
            path_strings = []  # OrderedDict()
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

            self.path = []
            self.closed_shapes = OrderedDict()
            # print("Starting========= {}".format(self.sf))
            for path_string, id_, clr in path_strings:
                # print(id_)
                move_found = False
                close_Found = False
                tmp = []
                self.closed_shapes[id_] = dict()
                self.closed_shapes[id_][id_ + "paths"] = []
                self.closed_shapes[id_][id_ + "shapes"] = []  # for drawing meshes
                self.closed_shapes[id_]["color"] = clr
                _path = parse_path(path_string)
                for e in _path:
                    # print(e)
                    self.path.append(e)

                    if isinstance(e, Close) or (isinstance(e, Move) and move_found):
                        self.closed_shapes[id_][id_ + "paths"].append(tmp)
                        move_found = False

                    if isinstance(e, Move):  # shape started
                        tmp = []
                        move_found = True

                    if not isinstance(e, Move) and move_found:
                        tmp.append(e)

                # print("============")

            # for id_, closed_paths in self.closed_shapes.items():
            #     print("========== id = {} =================".format(id_))
            #     for s in closed_paths[id_+"paths"]:
            #         print(s)
            #     print("====================================\n")

            self.psf = self.sf

        self._draw(animate)

    def _draw(self, animate):

        line_count = 0
        bezier_count = 0
        anim_list = []
        for id_, closed_paths in self.closed_shapes.items():
            # TODO: Support for other svg shapes like Arc, Circle, Text etc.

            for s in closed_paths[id_ + "paths"]:
                tmp = []
                for e in s:

                    if isinstance(e, Line):
                        lp = line_points(
                            e, *self.b.size, *self.b.pos, *self.sw_size, self.sf
                        )
                        setattr(self.b, "line{}_start_x".format(line_count), lp[0])
                        setattr(self.b, "line{}_start_y".format(line_count), lp[1])
                        setattr(
                            self.b,
                            "line{}_end_x".format(line_count),
                            lp[0] if animate else lp[2],
                        )
                        setattr(
                            self.b,
                            "line{}_end_y".format(line_count),
                            lp[1] if animate else lp[3],
                        )
                        setattr(
                            self.b,
                            "line{}_width".format(line_count),
                            1 if animate else self.LINE_WIDTH,
                        )

                        if animate:
                            anim_list.append(
                                Animation(
                                    d=self.DUR,
                                    **dict(
                                        zip(
                                            [
                                                "line{}_end_x".format(line_count),
                                                "line{}_end_y".format(line_count),
                                                "line{}_width".format(line_count),
                                            ],
                                            [lp[2], lp[3], self.LINE_WIDTH],
                                        )
                                    ),
                                )
                            )
                        line_count += 1

                        tmp.extend(lp)
                    if isinstance(e, CubicBezier):
                        bp = bezier_points(
                            e, *self.b.size, *self.b.pos, *self.sw_size, self.sf
                        )
                        setattr(self.b, "bezier{}_start_x".format(bezier_count), bp[0])
                        setattr(self.b, "bezier{}_start_y".format(bezier_count), bp[1])
                        setattr(
                            self.b,
                            "bezier{}_control1_x".format(bezier_count),
                            bp[0] if animate else bp[2],
                        )
                        setattr(
                            self.b,
                            "bezier{}_control1_y".format(bezier_count),
                            bp[1] if animate else bp[3],
                        )
                        setattr(
                            self.b,
                            "bezier{}_control2_x".format(bezier_count),
                            bp[0] if animate else bp[4],
                        )
                        setattr(
                            self.b,
                            "bezier{}_control2_y".format(bezier_count),
                            bp[1] if animate else bp[5],
                        )
                        setattr(
                            self.b,
                            "bezier{}_end_x".format(bezier_count),
                            bp[0] if animate else bp[6],
                        )
                        setattr(
                            self.b,
                            "bezier{}_end_y".format(bezier_count),
                            bp[1] if animate else bp[7],
                        )
                        setattr(
                            self.b,
                            "bezier{}_width".format(bezier_count),
                            1 if animate else self.LINE_WIDTH,
                        )

                        if animate:
                            anim_list.append(
                                Animation(
                                    d=self.DUR,
                                    **dict(
                                        zip(
                                            [
                                                "bezier{}_control1_x".format(
                                                    bezier_count
                                                ),
                                                "bezier{}_control1_y".format(
                                                    bezier_count
                                                ),
                                                "bezier{}_control2_x".format(
                                                    bezier_count
                                                ),
                                                "bezier{}_control2_y".format(
                                                    bezier_count
                                                ),
                                                "bezier{}_end_x".format(bezier_count),
                                                "bezier{}_end_y".format(bezier_count),
                                                "bezier{}_width".format(bezier_count),
                                            ],
                                            [
                                                bp[2],
                                                bp[3],
                                                bp[4],
                                                bp[5],
                                                bp[6],
                                                bp[7],
                                                self.LINE_WIDTH,
                                            ],
                                        )
                                    ),
                                )
                            )
                        bezier_count += 1

                        tmp.extend(
                            get_all_points(
                                (bp[0], bp[1]),
                                (bp[2], bp[3]),
                                (bp[4], bp[5]),
                                (bp[6], bp[7]),
                            )
                        )

                if tmp not in closed_paths[id_ + "shapes"]:
                    closed_paths[id_ + "shapes"].append(tmp)

        # for id_, closed_paths in self.closed_shapes.items():
        #     print("========== id = {} =================".format(id_))
        #     for s in closed_paths[id_+"shapes"]:
        #         print(s[:5])
        #     print("====================================\n")

        if animate:
            anim = anim_list[0]
            for a in anim_list[1:]:
                anim += a  # Only sequence animation working. Don't know why parallel not working :(

        if self.fill:
            setattr(self.b, "mesh_opacity", 0 if animate else 1)

            if animate:
                fill_anim = Animation(d=0.4, mesh_opacity=1)
                fill_anim.bind(on_progress=self.fill_up_shapes)
                anim += fill_anim

        if animate:
            anim.cancel_all(self.b)
            anim.bind(on_progress=self.update_canvas)

            anim.start(self.b)
        else:
            if not self.fill:
                self.update_canvas()
            else:
                self.b.canvas.clear()
                self.fill_up_shapes()

    def update_canvas(self, *args, **kwargs):
        self.b.canvas.clear()

        with self.b.canvas:
            Color(*self.LINE_COLOR)

            line_count = 0
            bezier_count = 0

            # Draw svg
            for e in self.path:
                # if isinstance(e, Move):
                #     initial_point = line_points(e)
                #     print("Got initial point: {}".format(initial_point))
                if isinstance(e, Line):
                    KivyLine(
                        points=[
                            getattr(self.b, "line{}_start_x".format(line_count)),
                            getattr(self.b, "line{}_start_y".format(line_count)),
                            getattr(self.b, "line{}_end_x".format(line_count)),
                            getattr(self.b, "line{}_end_y".format(line_count)),
                        ],
                        width=getattr(self.b, "line{}_width".format(line_count)),
                    )
                    line_count += 1
                if isinstance(e, CubicBezier):
                    KivyLine(
                        bezier=[
                            getattr(self.b, "bezier{}_start_x".format(bezier_count)),
                            getattr(self.b, "bezier{}_start_y".format(bezier_count)),
                            getattr(self.b, "bezier{}_control1_x".format(bezier_count)),
                            getattr(self.b, "bezier{}_control1_y".format(bezier_count)),
                            getattr(self.b, "bezier{}_control2_x".format(bezier_count)),
                            getattr(self.b, "bezier{}_control2_y".format(bezier_count)),
                            getattr(self.b, "bezier{}_end_x".format(bezier_count)),
                            getattr(self.b, "bezier{}_end_y".format(bezier_count)),
                        ],
                        width=getattr(self.b, "bezier{}_width".format(bezier_count)),
                    )
                    bezier_count += 1
                # if isinstance(e, Close):
                #     KivyLine(points=[*line_points(e),*initial_point], )
                #     print("Closing subpath from {} to {}".format(line_points(e), initial_point))

            # if self.fill:
            #     try:
            #         s = self.sf.split(".")[0] + ".png"
            #         Color(1, 1, 1, getattr(self.b, "image_opacity"))
            #         Rectangle(pos=self.b.pos, size=self.b.size, source=s)
            #     except:
            #         pass

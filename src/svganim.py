from kivy.graphics import Line as KivyLine, Bezier as KivyBezier, Color, Rectangle
from kivy.animation import Animation

from svg.path import parse_path
from svg.path.path import Line, CubicBezier, Close, Move
from xml.dom import minidom


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
        self.psf = None  # Previous svg file - Don't re-find path for same file in a row

    def animate(self, svg_file, *args, **kwargs):
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
            path_strings = [
                path.getAttribute("d") for path in doc.getElementsByTagName("path")
            ]
            doc.unlink()

            self.path = []
            for path_string in path_strings:
                _path = parse_path(path_string)
                for e in _path:
                    # print(e)
                    self.path.append(e)
                # print("============")

            self.psf = self.sf

        self._animate()

    def _animate(self):

        line_count = 0
        bezier_count = 0
        anim_list = []
        for i, e in enumerate(self.path):
            # TODO: Support for other svg shapes like Arc, Circle, Text etc.

            if isinstance(e, Line):
                lp = line_points(e, *self.b.size, *self.b.pos, *self.sw_size, self.sf)
                setattr(self.b, "line{}_start_x".format(line_count), lp[0])
                setattr(self.b, "line{}_start_y".format(line_count), lp[1])
                setattr(self.b, "line{}_end_x".format(line_count), lp[0])
                setattr(self.b, "line{}_end_y".format(line_count), lp[1])
                setattr(self.b, "line{}_width".format(line_count), 1)

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
            if isinstance(e, CubicBezier):
                bp = bezier_points(e, *self.b.size, *self.b.pos, *self.sw_size, self.sf)
                setattr(self.b, "bezier{}_start_x".format(bezier_count), bp[0])
                setattr(self.b, "bezier{}_start_y".format(bezier_count), bp[1])
                setattr(self.b, "bezier{}_control1_x".format(bezier_count), bp[0])
                setattr(self.b, "bezier{}_control1_y".format(bezier_count), bp[1])
                setattr(self.b, "bezier{}_control2_x".format(bezier_count), bp[0])
                setattr(self.b, "bezier{}_control2_y".format(bezier_count), bp[1])
                setattr(self.b, "bezier{}_end_x".format(bezier_count), bp[0])
                setattr(self.b, "bezier{}_end_y".format(bezier_count), bp[1])
                setattr(self.b, "bezier{}_width".format(bezier_count), 1)

                anim_list.append(
                    Animation(
                        d=self.DUR,
                        **dict(
                            zip(
                                [
                                    "bezier{}_control1_x".format(bezier_count),
                                    "bezier{}_control1_y".format(bezier_count),
                                    "bezier{}_control2_x".format(bezier_count),
                                    "bezier{}_control2_y".format(bezier_count),
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

        anim = anim_list[0]
        for a in anim_list[1:]:
            anim += a  # Only sequence animation working. Don't know why parallel not working :(

        if self.fill:
            setattr(self.b, "image_opacity", 0)
            image_anim = Animation(d=0.4, t="in_cubic", image_opacity=1)
            anim += image_anim

        anim.cancel_all(self.b)
        anim.bind(on_progress=self.update_canvas)
        anim.start(self.b)

    def update_canvas(self, *args, **kwargs):
        self.b.canvas.after.clear()

        with self.b.canvas.after:
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

            if self.fill:
                try:
                    s = self.sf.split(".")[0] + ".png"
                    Color(1, 1, 1, getattr(self.b, "image_opacity"))
                    Rectangle(pos=self.b.pos, size=self.b.size, source=s)
                except:
                    pass

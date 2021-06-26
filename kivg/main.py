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
from .animation import Animation
from kivy.utils import get_color_from_hex as gch
from kivy.properties import NumericProperty

from svg.path import parse_path
from svg.path.path import Line, CubicBezier, Close, Move
from xml.dom import minidom

from collections import OrderedDict

from .utils import x, y, point, line_points, bezier_points, get_all_points, parse_svg, find_center

class Kivg:
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
            Color(*color[:3], getattr(self.b, "mesh_opacity"))
            for vertices, indices in meshes:
                Mesh(vertices=vertices, indices=indices, mode="triangle_fan")

    def fill_up_shapes(self, *args):
        for id_, closed_paths in self.closed_shapes.items():
            c = self.closed_shapes[id_]["color"]
            self.fill_up(closed_paths[id_ + "shapes"], c)
    
    def fill_up_shapes_anim(self, shapes, *args):
        for shape in shapes:
            c = shape[0]
            self.fill_up([shape[1]], c)
    
    def anim_on_comp(self, *args):
        self.curr_count+=1
        self.prev_shapes.append(self.curr_shape)
        if self.curr_count<len(self.all_anim):
            id_, a = self.all_anim[self.curr_count]
            setattr(self, "curr_id", id_)
            setattr(self, "curr_clr", self.closed_shapes[id_]["color"])
            a.bind(on_progress=self.track_progress)
            a.start(self.b)
    
    def shape_animate(self, svg_file, anim_config_list=[], on_complete=None):
        """
        svg_file: svg file name

        anim_config_list: a list of dicts with keys id_ to animate and from_, the direction of animation

        on_complete: optional function to call after total completion
        """
        self.draw(svg_file, from_shape_anim=True)
        setattr(self.b, "mesh_opacity", 1)

        self.all_anim = []
        self.curr_count= 0
        for i, config in enumerate(anim_config_list):
            # setattr(self, "{}_".format(config["id_"]), config["id_"])
            anim_list = self._shape_animate(
                config["id_"],
                config.get("from_", None),
                config.get("t", "out_sine"),
                config.get("d", .3),
                )
            
            if anim_list:
                anim = anim_list[0]
                for a in anim_list[1:]:
                    anim&= a
                anim.bind(on_complete= self.anim_on_comp )
                self.all_anim.append((config["id_"], anim))
            else:
                setattr(self, "curr_id", config["id_"])
                setattr(self, "curr_clr", self.closed_shapes[config["id_"]]["color"])
                self.track_progress()
        
        id_, a = self.all_anim[0]
        setattr(self, "curr_id", id_)
        setattr(self, "curr_clr", self.closed_shapes[id_]["color"])

        a.cancel_all(self.b)
        a.bind(on_progress=self.track_progress)
        if on_complete:
            self.all_anim[-1][1].bind(on_complete=on_complete)
        
        a.start(self.b)
    
    def _shape_animate(self, id_, from_, t, d):
        line_count = 0
        bezier_count = 0
        anim_list = []
        self.prev_shapes = []
        self.curr_shape = []
        if self.closed_shapes.get(id_, None):
            tmp = []
            for s in self.closed_shapes[id_][id_ + "paths"]:
                tmp2 = []
                for e in s:
                    if isinstance(e, Line):
                        lp = line_points(
                            e, *self.b.size, *self.b.pos, *self.sw_size, self.sf
                        )
                        tmp2.append([
                            (lp[0], lp[1]),
                            (lp[2], lp[3])
                        ])

                    if isinstance(e, CubicBezier):
                        bp = bezier_points(
                            e, *self.b.size, *self.b.pos, *self.sw_size, self.sf
                        )
                        tmp2.append([
                            (bp[0], bp[1]),
                            (bp[2], bp[3]),
                            (bp[4], bp[5]),
                            (bp[6], bp[7])
                        ])
                        
                # print(tmp2)
                tmp.append(tmp2)
            # s = self.closed_shapes[id_][id_ + "shapes"]
            # print(c)
            # print(len(s[0]))
            l = []
            for each in tmp:
                for e in each:
                    for i in e: l.append(i[0]) if from_ in ("left", "right", "center_x") else l.append(i[1])
            

            if from_ in ("top", "right"):
                base_point = max(l) # rightmost/topmost point to start animation from
            elif from_ in ("left", "bottom"):
                base_point = min(l) # leftmost/bottommost point to start animation from
            elif from_ in ("center_x", "center_y"):
                base_point = find_center(sorted(l))

            for each in tmp:
                for e in each:
                    if len(e)==2: #Line
                        setattr(self.b, "{}_mesh_line{}_start_x".format(id_, line_count), base_point if from_ in ("left", "right", "center_x") else e[0][0])
                        setattr(self.b, "{}_mesh_line{}_start_y".format(id_, line_count), base_point if from_ in ("top", "bottom", "center_y") else e[0][1])
                        setattr(
                            self.b,
                            "{}_mesh_line{}_end_x".format(id_, line_count), base_point if from_ in ("left", "right", "center_x") else e[1][0]
                        )
                        setattr(
                            self.b,
                            "{}_mesh_line{}_end_y".format(id_, line_count),
                            base_point if from_ in ("top", "bottom", "center_y") else e[1][1],
                        )

                        if from_ in ("left", "right", "center_x"):
                            anim_list.append(
                                Animation(
                                    d=d,
                                    t=t,
                                    **dict(
                                        zip(
                                            [
                                                "{}_mesh_line{}_start_x".format(id_, line_count),
                                                "{}_mesh_line{}_end_x".format(id_, line_count),
                                            ],
                                            [e[0][0], e[1][0]],
                                        )
                                    ),
                                )
                            )
                        else:
                            anim_list.append(
                                Animation(
                                    d=d, #if from_ else 0
                                    t=t,
                                    **dict(
                                        zip(
                                            [
                                                "{}_mesh_line{}_start_y".format(id_, line_count),
                                                "{}_mesh_line{}_end_y".format(id_, line_count),
                                            ],
                                            [e[0][1], e[1][1]],
                                        )
                                    ),
                                )
                            )

                        line_count += 1

                    if len(e)==4: #Bezier
                        setattr(self.b, "{}_mesh_bezier{}_start_x".format(id_, bezier_count), base_point if from_ in ("left", "right", "center_x") else e[0][0])
                        setattr(self.b, "{}_mesh_bezier{}_start_y".format(id_, bezier_count), base_point if from_ in ("top", "bottom", "center_y") else e[0][1])
                        setattr(
                            self.b,
                            "{}_mesh_bezier{}_control1_x".format(id_, bezier_count),
                            base_point if from_ in ("left", "right", "center_x") else e[1][0],
                        )
                        setattr(
                            self.b,
                            "{}_mesh_bezier{}_control1_y".format(id_, bezier_count),
                            base_point if from_ in ("top", "bottom", "center_y") else e[1][1],
                        )
                        setattr(
                            self.b,
                            "{}_mesh_bezier{}_control2_x".format(id_, bezier_count),
                            base_point if from_ in ("left", "right", "center_x") else e[2][0],
                        )
                        setattr(
                            self.b,
                            "{}_mesh_bezier{}_control2_y".format(id_, bezier_count),
                            base_point if from_ in ("top", "bottom", "center_y") else e[2][1],
                        )
                        setattr(
                            self.b,
                            "{}_mesh_bezier{}_end_x".format(id_, bezier_count),
                            base_point if from_ in ("left", "right", "center_x") else e[3][0],
                        )
                        setattr(
                            self.b,
                            "{}_mesh_bezier{}_end_y".format(id_, bezier_count),
                            base_point if from_ in ("top", "bottom", "center_y") else e[3][1],
                        )

                        if from_ in ("left", "right", "center_x"):
                            anim_list.append(
                                Animation(
                                    d=d,
                                    t=t,
                                    **dict(
                                        zip(
                                            [
                                                "{}_mesh_bezier{}_start_x".format(
                                                    id_, bezier_count
                                                ),
                                                "{}_mesh_bezier{}_control1_x".format(
                                                    id_, bezier_count
                                                ),
                                                "{}_mesh_bezier{}_control2_x".format(
                                                    id_, bezier_count
                                                ),
                                                "{}_mesh_bezier{}_end_x".format(id_, bezier_count),
                                            ],
                                            [
                                                e[0][0],
                                                e[1][0],
                                                e[2][0],
                                                e[3][0],
                                            ],
                                        )
                                    ),
                                )
                            )
                        else:
                            anim_list.append(
                                Animation(
                                    d=d, #if from_ else 0
                                    t=t,
                                    **dict(
                                        zip(
                                            [
                                                "{}_mesh_bezier{}_start_y".format(
                                                    id_, bezier_count
                                                ),
                                                "{}_mesh_bezier{}_control1_y".format(
                                                    id_, bezier_count
                                                ),
                                                "{}_mesh_bezier{}_control2_y".format(
                                                    id_, bezier_count
                                                ),
                                                "{}_mesh_bezier{}_end_y".format(id_, bezier_count),
                                            ],
                                            [
                                                e[0][1],
                                                e[1][1],
                                                e[2][1],
                                                e[3][1],
                                            ],
                                        )
                                    ),
                                )
                            )
                        bezier_count += 1

            setattr(self, "{}_tmp".format(id_), tmp)
            return anim_list
    
    def track_progress(self, *args):
        
        id_ = getattr(self, "curr_id")
        shape_list = []
        line_count = 0
        bezier_count = 0
        for each in getattr(self, "{}_tmp".format(id_)):
            for e in each:
                x =  []
                if len(e)==2: #Line
                    shape_list.extend([
                        getattr(self.b, "{}_mesh_line{}_start_x".format(id_, line_count)),
                        getattr(self.b, "{}_mesh_line{}_start_y".format(id_, line_count)),
                        getattr(self.b, "{}_mesh_line{}_end_x".format(id_, line_count)),
                        getattr(self.b, "{}_mesh_line{}_end_y".format(id_, line_count))
                    ])
                
                    line_count += 1

                if len(e)==4: #Bezier
                    shape_list.extend(
                        get_all_points(
                            (   getattr(self.b, "{}_mesh_bezier{}_start_x".format(id_, bezier_count)),
                                getattr(self.b, "{}_mesh_bezier{}_start_y".format(id_, bezier_count))),
                            (
                                getattr(self.b, "{}_mesh_bezier{}_control1_x".format(id_, bezier_count)),
                                getattr(self.b, "{}_mesh_bezier{}_control1_y".format(id_, bezier_count))
                            ),
                            (
                                getattr(self.b, "{}_mesh_bezier{}_control2_x".format(id_, bezier_count)),
                                getattr(self.b, "{}_mesh_bezier{}_control2_y".format(id_, bezier_count))
                            ),
                            (
                                getattr(self.b, "{}_mesh_bezier{}_end_x".format(id_, bezier_count)),
                                getattr(self.b, "{}_mesh_bezier{}_end_y".format(id_, bezier_count))
                            )
                        )
                    )
                    bezier_count += 1
        
        # print(shape_list[:5])
        self.b.canvas.clear()
        self.curr_shape = (getattr(self, "curr_clr"), shape_list)
        s = [*self.prev_shapes, self.curr_shape]
        self.fill_up_shapes_anim(s)


    def draw(self, svg_file, animate=False, anim_type="seq", *args, **kwargs):
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

        anim_type: "seq"/"par" for sequence/parallel
        """
        self.fill = kwargs.get("fill", self._fill)
        self.LINE_WIDTH = kwargs.get("line_width", self._LINE_WIDTH)
        self.LINE_COLOR = kwargs.get("line_color", self._LINE_COLOR)
        self.DUR = kwargs.get("dur", self._DUR)
        from_shape_anim = kwargs.get("from_shape_anim", False)
        anim_type = anim_type if anim_type in ("seq", "par") else "seq"

        self.sf = svg_file
        if self.sf != self.psf:
            self.sw_size, path_strings = parse_svg(svg_file)

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

        anim_list = self._calc_paths(animate)
        if not from_shape_anim:
            if animate:
                anim = anim_list[0]
                for a in anim_list[1:]:
                    if anim_type=="seq":
                        anim += a
                    else: anim &= a

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

    def _calc_paths(self, animate):

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
        # uncomment krna hai
        # if not shape_anim:
        # print(anim_list)
        return anim_list

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

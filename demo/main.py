from kivy.app import App
from kivy.lang import Builder
from kivy.clock import mainthread

from kivg import Kivg

kv = """
BoxLayout:
    orientation: "vertical"
    canvas:
        Color:
            rgba: 1,1,1,1
        Rectangle:
            pos: self.pos
            size: self.size

    AnchorLayout:
        BoxLayout:
            id: svg_area
            size_hint: None, None
            size: 256, 256
    
    GridLayout:
        size_hint_y: None
        height: dp(64)
        id: button_area
        rows: 1
        padding: dp(4), 0
        spacing: dp(root.width/40)

        MYMDIconButton:
            svg_icon: "icons/kivy.svg"
        
        MYMDIconButton:
            svg_icon: "icons/python2.svg"
        
        MYMDIconButton:
            svg_icon: "icons/github3.svg"
        
        MYMDIconButton:
            svg_icon: "icons/github.svg"
        
        MYMDIconButton:
            svg_icon: "icons/sublime.svg"
        
        MYMDIconButton:
            svg_icon: "icons/discord2.svg"
        
        MYMDIconButton:
            svg_icon: "icons/so.svg"
        
        MYMDIconButton:
            svg_icon: "icons/text.svg"
        
        MYMDIconButton:
            svg_icon: "icons/twitter2.svg"
        
        MYMDIconButton:
            svg_icon: "icons/google3.svg"
        
        MYMDIconButton:
            svg_icon: "icons/pie_chart.svg"
        
        MYMDIconButton:
            svg_icon: "icons/facebook2.svg"

<MYMDIconButton@Button>:
    size_hint: None, None
    size: dp(48), dp(48)
    on_release:
        app.animate(self.svg_icon) if (not "so" in self.svg_icon) and (not "pie" in self.svg_icon) and (not "text" in self.svg_icon)\
            else app.shape_animate(self.svg_icon, self.svg_icon[6:-4]+'_config')

"""


class KivgDemo(App):
    def build(self):
        self.root = Builder.load_string(kv)
        self.s = Kivg(self.root.ids.svg_area)
        return self.root

    @mainthread
    def show_button_icon(self, *args):
        grid = self.root.ids.button_area
        for b in grid.children:
            s = Kivg(b)
            setattr(b, "s", s)
            self.draw_filled(s, b.svg_icon)

    def draw_filled(self, s, icon):
        s.draw(icon)

    def draw_path(self, s, icon):
        s.draw(icon, fill=False, line_width=1)

    def on_start(self):
        self.show_button_icon()

    def animate(self, svg_file):
        self.s.draw(svg_file, animate=True, fill=True, line_width=1)
    
    def shape_animate(self, svg_file, config):
        self.sf = svg_file
        self.con = config
        pie_chart_config = [
            {"id_":"neck", "from_":"center_y","d":.45, "t":"out_cubic"},
            {"id_":"neck-color","d":0},
            {"id_":"stand", "from_":"center_x", "t":"out_back", "d":.45},
            {"id_":"stand-color", "d":0},
            {"id_":"display", "from_":"center_x", "t":"out_bounce","d":.45},
            {"id_":"display-color","d":0},
            {"id_":"screen", "from_":"center_y", "t":"out_circ","d":.45},
            {"id_":"screen-color", "from_":"left","d":.1},
            {"id_":"bullet1", "from_":"center_x", "d":.2},
            {"id_":"data1", "from_":"left", "d":.3},
            {"id_":"bullet2", "from_":"center_x", "d":.2},
            {"id_":"data2", "from_":"left", "d":.3},
            {"id_":"bullet3", "from_":"center_x", "d":.2},
            {"id_":"data3", "from_":"left", "d":.3},
            {"id_":"pie-full", "from_":"center_y"},
            {"id_":"pie", "from_":"bottom", "t":"out_bounce", "d":.1},
            {"id_":"btn1", "from_": "left"},
            {"id_":"btn2", "from_":"right"},
        ]

        so_config = [
            {"id_": "base", "from_":"center_y", "t":"out_bounce", "d":.4},
            {"id_":"line1", "d":.05},
            {"id_":"line2", "d":.05},
            {"id_":"line3", "d":.05},
            {"id_":"line4", "d":.05},
            {"id_":"line5", "d":.05},
            {"id_":"line6", "d":.05},
        ]

        text_config = [
            {"id_":"k","from_":"center_x", "t":"out_back", "d":.4},
            {"id_":"i","from_":"center_y", "t":"out_bounce", "d":.4},
            {"id_":"v","from_":"top", "t":"out_quint", "d":.4},
            {"id_":"y","from_":"bottom", "t":"out_back", "d":.4}
        ]
        self.s.shape_animate(svg_file, anim_config_list=eval(config), on_complete=self.completed)
    
    def completed(self, *args):
        pass
        # Repeat animation
        # Clock.schedule_once(lambda *args: self.shape_animate(self.sf, self.con), .5)


if __name__ == "__main__":
    KivgDemo().run()

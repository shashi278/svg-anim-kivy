from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock

from svganim import SVGAnimation

kv = """
BoxLayout:
    orientation: "vertical"

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
            svg_icon: "icons/text2.svg"
        
        MYMDIconButton:
            svg_icon: "icons/twitter2.svg"
        
        MYMDIconButton:
            svg_icon: "icons/google3.svg"
        
        MYMDIconButton:
            svg_icon: "icons/pie-chart.svg"
        
        MYMDIconButton:
            svg_icon: "icons/facebook2.svg"

<MYMDIconButton@MDIconButton>:
    on_press: app.draw_path(self.s, self.svg_icon)
    on_release:
        app.draw_filled(self.s, self.svg_icon);app.animate(self.svg_icon.split(".")[0]+".svg")

"""

import threading


class SVGAnimationDemo(MDApp):
    def build(self):
        self.root = Builder.load_string(kv)
        self.s = SVGAnimation(self.root.ids.svg_area)
        return self.root

    def show_button_icon(self, *args):
        grid = self.root.ids.button_area
        for b in grid.children:
            s = SVGAnimation(b)
            setattr(b, "s", s)
            self.draw_filled(s, b.svg_icon)

    def draw_filled(self, s, icon):
        s.draw(icon)

    def draw_path(self, s, icon):
        s.draw(icon, fill=False, line_width=1)

    def on_start(self):
        t = threading.Thread(target=self.show_button_icon)
        Clock.schedule_once(lambda *args: t.start())

    def animate(self, svg_file):
        self.s.draw(svg_file, fill=True, animate=False, line_width=1)


if __name__ == "__main__":
    SVGAnimationDemo().run()

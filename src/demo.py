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
            icon: "icons/kivy.png"
        
        MYMDIconButton:
            icon: "icons/python2.png"
        
        MYMDIconButton:
            icon: "icons/github3.png"
        
        MYMDIconButton:
            icon: "icons/github.png"
        
        MYMDIconButton:
            icon: "icons/sublime.png"
        
        MYMDIconButton:
            icon: "icons/discord.png"
        
        MYMDIconButton:
            icon: "icons/so.png"
        
        MYMDIconButton:
            icon: "icons/travis.png"
        
        MYMDIconButton:
            icon: "icons/twitter2.png"
        
        MYMDIconButton:
            icon: "icons/google3.png"
        
        MYMDIconButton:
            icon: "icons/facebook2.png"
        
        MYMDIconButton:
            icon: "icons/instagram2.png"

<MYMDIconButton@MDIconButton>:
    on_release:
        app.animate(self.icon.split(".")[0]+".svg")

"""


class SVGAnimationDemo(MDApp):
    def build(self):
        root = Builder.load_string(kv)
        self.s = SVGAnimation(root.ids.svg_area)
        return root

    def on_start(self):
        Clock.schedule_once(lambda *args: self.animate("icons/text2.svg"), 1)

    def animate(self, svg_file):
        self.s.animate(svg_file)


if __name__ == "__main__":
    SVGAnimationDemo().run()

from kivy.app import App
from kivy.uix.widget import Widget
from kivg import Kivg

class MyWidget(Widget):
    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        self.size = (1024, 1024)
        self.pos = (0, 0)

class KivgDemoApp(App):
    def build(self):
        widget = MyWidget()
        self.kivg = Kivg(widget)
        self.kivg.draw("icons/so.svg", animate=True, line_color=[1,1,1,1], line_width=2)
        return widget

if __name__ == "__main__":
    KivgDemoApp().run()
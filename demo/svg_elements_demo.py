"""
Demo showcasing SVG elements support in Kivg.

This demo application displays a simple SVG with various element types
including circles, rectangles, and ellipses.
"""
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivg import Kivg
from kivy.core.window import Window

Window.size = (800, 800)  # Set the window size for the demo

# Create an SVG with various elements
SVG_CONTENT = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="600">
    <!-- Circle -->
    <circle cx="150" cy="100" r="50" fill="red" stroke="black" stroke-width="2" />
    
    <!-- Rectangle -->
    <rect x="250" y="50" width="100" height="100" fill="blue" stroke="black" stroke-width="2" />
    
    <!-- Rounded Rectangle -->
    <rect x="400" y="50" width="100" height="100" rx="20" ry="20" fill="green" stroke="black" stroke-width="2" />
    
    <!-- Ellipse -->
    <ellipse cx="600" cy="100" rx="75" ry="50" fill="purple" stroke="black" stroke-width="2" />
    
    <!-- Path with line segments -->
    <path d="M100,250 L200,300 L150,350 Z" fill="yellow" stroke="black" stroke-width="2" />
    
    <!-- Path with bezier curve -->
    <path d="M300,250 C350,200 450,200 500,250 S600,350 650,300" fill="none" stroke="orange" stroke-width="3" />
</svg>
"""

def save_svg_file():
    """Save the SVG content to a file."""
    svg_file = "svg_elements_demo.svg"
    # with open(svg_file, "w") as f:
    #     f.write(SVG_CONTENT)
    return os.path.abspath(svg_file)


class SVGElementsDemo(BoxLayout):
    """Main demo layout showcasing SVG elements support."""
    
    def __init__(self, **kwargs):
        super(SVGElementsDemo, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Create the SVG file
        self.svg_file = save_svg_file()
        
        # Create layout
        title = Label(
            text='SVG Elements Demo',
            size_hint=(1, 0.1),
            font_size='20sp'
        )
        self.add_widget(title)
        
        # Float layout for the SVG rendering
        self.float_layout = BoxLayout(size_hint=(0.8, 0.8))
        # self.float_layout.size = (1024, 1024)
        # self.float_layout.pos = (0, 0)

        # with self.float_layout.canvas.before:
        #     from kivy.graphics import Color, Rectangle
        #     Color(1, 1, 1, 1)  # White background
        #     Rectangle(pos=self.float_layout.pos, size=self.float_layout.size)
        
        self.add_widget(self.float_layout)
        
        # Button layout
        button_layout = BoxLayout(
            size_hint=(1, 0.1),
            spacing=10
        )
        
        load_btn = Button(
            text='Load SVG',
            on_press=self.load_svg
        )
        animate_btn = Button(
            text='Animate SVG',
            on_press=self.animate_svg
        )
        
        button_layout.add_widget(load_btn)
        button_layout.add_widget(animate_btn)
        self.add_widget(button_layout)
        
        # Initialize Kivg instance with the float_layout widget
        self.kivg = None
    
    def load_svg(self, *args):
        """Load the SVG without animation."""
        self.float_layout.canvas.clear()
        # Create a new instance for the current rendering
        self.kivg = Kivg(self.float_layout)
        self.kivg.draw(self.svg_file, animate=False)
    
    def animate_svg(self, *args):
        """Load the SVG with animation."""
        self.float_layout.clear_widgets()
        # Create a new instance for the current rendering
        self.kivg = Kivg(self.float_layout)
        self.kivg.draw(self.svg_file, animate=True, dur=0.02)


class SVGElementsDemoApp(App):
    """SVG Elements demo application."""
    
    def build(self):
        se = SVGElementsDemo()
        # with se.float_layout.canvas.before:
        #     from kivy.graphics import Color, Rectangle
        #     Color(1, 1, 1, 1)  # White background
        #     Rectangle(pos=se.float_layout.pos, size=se.float_layout.size)
        return se


if __name__ == '__main__':
    SVGElementsDemoApp().run() 
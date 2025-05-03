#!/usr/bin/env python3
"""
Path Tracking Animation Demo

This example demonstrates how to use the path tracking feature
to animate SVG elements along SVG paths.
"""
import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from kivg.main import Kivg

DEMO_SVG = os.path.join(os.path.dirname(__file__), "icons", "path_tracking_demo.svg")


class PathTrackingDemo(App):
    """Demo app for SVG path tracking animation."""
    
    def build(self):
        """Build the app UI."""
        # Main layout
        layout = BoxLayout(orientation='vertical')
        
        # SVG drawing area
        self.drawing_area = FloatLayout(size_hint=(1, 0.8))
        
        # Button controls
        controls = BoxLayout(size_hint=(1, 0.2))
        
        # Buttons for different animations
        circle_btn = Button(
            text='Animate Circle', 
            on_press=self.animate_circle
        )
        rect_btn = Button(
            text='Animate Rectangle', 
            on_press=self.animate_rect
        )
        ellipse_btn = Button(
            text='Animate Ellipse', 
            on_press=self.animate_ellipse
        )
        repeat_btn = Button(
            text='Repeat Animation', 
            on_press=self.repeat_animation
        )
        rotate_btn = Button(
            text='Rotate Animation', 
            on_press=self.rotate_animation
        )
        
        # Add buttons to controls
        controls.add_widget(circle_btn)
        controls.add_widget(rect_btn)
        controls.add_widget(ellipse_btn)
        controls.add_widget(repeat_btn)
        controls.add_widget(rotate_btn)
        
        # Add widgets to main layout
        layout.add_widget(self.drawing_area)
        layout.add_widget(controls)
        
        # Create Kivg instance for SVG rendering
        self.kivg = Kivg(self.drawing_area)
        
        # Initial SVG drawing
        self.kivg.draw(DEMO_SVG, fill=True)
        
        # Set window size
        Window.size = (800, 600)
        
        return layout
    
    def animate_circle(self, instance):
        """Animate a circle along a path."""
        # Reset by redrawing the SVG
        self.kivg.draw(DEMO_SVG, fill=True)
        
        # Animate circle element along the path
        self.kivg.animate_element_along_path(
            element_id="circle1",  # ID of the circle element
            path_id="path1",       # ID of the path to follow
            duration=3.0,          # Animation duration in seconds
            repeat=False,          # Don't repeat
            rotate=False           # Don't rotate
        )
    
    def animate_rect(self, instance):
        """Animate a rectangle along a path."""
        # Reset by redrawing the SVG
        self.kivg.draw(DEMO_SVG, fill=True)
        
        # Animate rectangle element along the path
        self.kivg.animate_element_along_path(
            element_id="rect1",    # ID of the rectangle element
            path_id="path1",       # ID of the path to follow
            duration=3.0,          # Animation duration in seconds
            repeat=False,          # Don't repeat
            rotate=False           # Don't rotate
        )
    
    def animate_ellipse(self, instance):
        """Animate an ellipse along a path."""
        # Reset by redrawing the SVG
        self.kivg.draw(DEMO_SVG, fill=True)
        
        # Animate ellipse element along the path
        self.kivg.animate_element_along_path(
            element_id="ellipse1", # ID of the ellipse element
            path_id="path1",       # ID of the path to follow
            duration=3.0,          # Animation duration in seconds
            repeat=False,          # Don't repeat
            rotate=False           # Don't rotate
        )
    
    def repeat_animation(self, instance):
        """Animate a circle along a path with repeat."""
        # Reset by redrawing the SVG
        self.kivg.draw(DEMO_SVG, fill=True)
        
        # Animate circle element along the path with repeat
        self.kivg.animate_element_along_path(
            element_id="circle1",  # ID of the circle element
            path_id="path1",       # ID of the path to follow
            duration=3.0,          # Animation duration in seconds
            repeat=True,           # Repeat the animation
            rotate=False           # Don't rotate
        )
    
    def rotate_animation(self, instance):
        """Animate a rectangle along a path with rotation."""
        # Reset by redrawing the SVG
        self.kivg.draw(DEMO_SVG, fill=True)
        
        # Animate rectangle element along the path with rotation
        self.kivg.animate_element_along_path(
            element_id="rect1",    # ID of the rectangle element
            path_id="path1",       # ID of the path to follow
            duration=3.0,          # Animation duration in seconds
            repeat=True,           # Repeat the animation
            rotate=True            # Rotate to follow path direction
        )


if __name__ == "__main__":
    PathTrackingDemo().run()
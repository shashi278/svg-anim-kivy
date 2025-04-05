## Kivg
*SVG path drawing and animation support in kivy application*

[![build](https://travis-ci.com/shashi278/svg-anim-kivy.svg?branch=main)](https://travis-ci.org/github/shashi278/svg-anim-kivy/) [![Python 3.6](https://img.shields.io/pypi/pyversions/kivymd)](https://www.python.org/downloads/release/python-360/) [![pypi](https://img.shields.io/pypi/v/kivg)](https://pypi.org/project/Kivg/) [![license](https://img.shields.io/github/license/shashi278/svg-anim-kivy)](https://github.com/shashi278/svg-anim-kivy/blob/main/LICENSE) [![downloads](https://img.shields.io/pypi/dm/kivg)](https://pypi.org/project/Kivg/) [![code size](https://img.shields.io/github/languages/code-size/shashi278/svg-anim-kivy)]()

#

## Features
| **Path Drawing & filling** | **Shape Animation** |
| :-------------: |:-------------:|
| <img src="https://raw.githubusercontent.com/shashi278/svg-anim-kivy/main/demo/svg_demo.gif" width=300> | <img src="https://raw.githubusercontent.com/shashi278/svg-anim-kivy/main/demo/adv_svg_anim.gif" width=300> |

Now you can take some of the advantages svg offers, in your kivy apps. Those are:
- [x] Compact file size compare to other formats - reduced asset size
- [x] Scalability - Draw them big or small
- [x] Interactivity - Animations

#

## Install
```bash
pip install kivg
```

## Usage Guide

Kivg helps you easily draw and animate SVG files in your Kivy applications.

### Path Drawing and Filling

```python
from kivg import Kivg

s = Kivg(my_widget)

# call draw method with a `svg_file` name
s.draw("github.svg", fill=False, animate=True, anim_type="seq")
```

#### Parameters:
- **fill** : *Whether to fill the shape after drawing*. Defaults to `True`
- **animate** : *Whether to animate drawing*. Defaults to `False`
- **anim_type** : *Whether to draw in sequence or parallel. Available `"seq"` and `"par"`*. Defaults to `"seq"`
- **line_width** : *Width of the path stroke*. Defaults to `2`
- **line_color** : *Color of the path stroke in RGBA format*. Defaults to `[0, 0, 0, 1]`
- **dur** : *Duration of each animation step in seconds*. Defaults to `0.02`

#### Important:
- Fill color would only work if it's in hex and inside `<path>` tag. You must modify svg if it's not this way already.
- Gradient is not yet supported - default to `#ffffff` if can't parse color

#

### Shape Animation

```python
from kivg import Kivg

s = Kivg(my_widget)

anim_config = [
    { "id_":"k", "from_":"center_x", "t":"out_back",   "d":.4 },
    { "id_":"i", "from_":"center_y", "t":"out_bounce", "d":.4 },
    { "id_":"v", "from_":"top",      "t":"out_quint",  "d":.4 },
    { "id_":"y", "from_":"bottom",   "t":"out_back",   "d":.4 }
]

# call shape_animate method with `svg_file` and an animation config list and optional callback
s.shape_animate("text.svg", anim_config_list=anim_config, on_complete=lambda *args: print("Completed!"))
```

#### Animation Configuration:
- **anim_config_list** : A list of dicts where each dict contain config for an `id`. Description of each key:
    - `"id_"` : `id` of svg `<path>` tag. It's required so each dict must contain `"id_"` key
    - `"from_"` : Direction from which a path should grow. Accepted values `"left"`, `"right"`, `"top"`, `"bottom"`, `"center_x"`(grow from center along horizontal axis), `"center_y"`, and `None`(Draw without animation). Defaults to `None`.
    - `"t"` : [Animation transition](https://kivy.org/doc/stable/api-kivy.animation.html?highlight=animation#kivy.animation.AnimationTransition). Defaults to `"out_sine"`.
    - `"d"` : Duration of animation. It'll still in-effect if `"from_"` is set to `None`. Defaults to .3

- **on_complete** (optional) : Function to call after entire animation is finished. It can be used to create looping animation

#### Important:
- You must add a unique `id` to each path element you want to animate
- Dictionary order in the list is important - animations run in the sequence provided
- Animations can be chained by using the on_complete callback for continuous effects

## Project Structure

The project is organized into the following main components:

```
kivg/
├── __init__.py         # Package entry point
├── data_classes.py     # Data structures for animation contexts
├── main.py             # Core Kivg class implementation
├── mesh_handler.py     # Handles mesh rendering 
├── path_utils.py       # SVG path utilities
├── svg_parser.py       # SVG parsing functionality
├── svg_renderer.py     # SVG rendering engine
├── version.py          # Version information
├── animation/          # Animation subsystem
│   ├── animation_shapes.py  # Shape-specific animations
│   ├── handler.py           # Animation coordination
│   └── kivy_animation.py    # Kivy animation file with some modifications
└── drawing/            # Drawing subsystem
    └── manager.py      # Drawing management
```

## Quick Start

1. **Install the package**:
   ```bash
   pip install kivg
   ```

2. **Set up your Kivy widget**:
   ```python
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
   ```

3. **Try shape animations**:
   ```python
   # Configure animations for different shapes
   animations = [
       {"id_": "shape1", "from_": "left", "t": "out_bounce", "d": 0.5},
       {"id_": "shape2", "from_": "top", "t": "out_elastic", "d": 0.3}
   ]
   self.kivg.shape_animate("path/to/your.svg", anim_config_list=animations)
   ```

## Useful Tools

Few links that I found useful for modifying few svg files in order to work with this library are:

* https://itchylabs.com/tools/path-to-bezier/ - Convert SVG Path to Cubic Curves

    Use it to convert SVG Arcs to Cubic Bezier. Make sure you paste the entire `path` in the textfield rather than only the arc section. Also you should provide path dimensions(`W` & `H`) on the website as your svg width and height(found under `<svg>` tag). You may also need to close each path, i.e. add `Z` at the end of new converted path.

* https://codepen.io/thednp/pen/EgVqLw - Convert Relative SVG Path To Absolute Path
    
    Maybe useful when you want to split a single svg path into multiple paths for animation purpose. Paste the entire path. When splitting, make sure you close the previous path by adding a `Z` at the end in the path string.

* https://jakearchibald.github.io/svgomg/ - SVG Optimizer
    
    Useful for cleaning up and optimizing SVG files to ensure compatibility.

## Changelog

**v1.1**
* Fixed crashing when SVG size is not int

**v1.0**
* Shape animation feature added
* Added `anim_type` in draw method

**Earlier Changes**
* Added option to draw image without animation, `animate=False`
* Added option to draw empty or filled path, `fill=True` or `fill=False`

## Contributing

![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)

We welcome contributions! Here's how you can help:

1. **Bug fixes**: If you find a bug, please open an issue or submit a pull request with a fix
2. **Feature additions**: Have an idea for a new feature? Open an issue to discuss it
3. **Documentation**: Improvements to documentation are always appreciated
4. **Examples**: Add more example use cases to help others learn

Please make sure to test your changes before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/shashi278/svg-anim-kivy/blob/main/LICENSE) file for details.

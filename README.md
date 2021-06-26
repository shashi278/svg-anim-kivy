## Kivg
*SVG path drawing and animation support in kivy application*

[![build](https://travis-ci.org/shashi278/svg-anim-kivy.svg?branch=main)](https://travis-ci.org/github/shashi278/svg-anim-kivy/) [![Python 3.6](https://img.shields.io/pypi/pyversions/kivymd)](https://www.python.org/downloads/release/python-360/) [![pypi](https://img.shields.io/pypi/v/kivg)](https://pypi.org/project/Kivg/) [![license](https://img.shields.io/pypi/l/kivg)](https://github.com/shashi278/svg-anim-kivy/blob/main/LICENSE) [![downloads](https://img.shields.io/pypi/dm/kivg)](https://pypi.org/project/Kivg/) [![code size](https://img.shields.io/github/languages/code-size/shashi278/svg-anim-kivy)]()

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

## How to use?
- ### Path drawing and filling

    ```python
    s = Kivg(my_widget)

    # call draw method with a `svg_file` name
    s.draw("github.svg", fill=False, animate=True, anim_type="seq")

    ```
    #### Info:
    - **fill** : *Whether to fill the shape after drawing*. Defaults to `True`

    - **animate** : *Whether to animate drawing*. Defaults to `False`

    - **anim_type** : *Whether to draw in sequence or parallel. Available `"seq"` and `"par"`*. Defaults to `"seq"`

    #### Important:
    - Fill color would only work if it's in hex and inside `<path>` tag. You must modify svg if it's not this way already.

    - Gradient is not yet supported - default to `#ffffff` if can't parse color
    #
- ### Shape Animation
    ```python
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
    #### Info:
    - **anim_config_list** : A list of dicts where each dict contain config for an `id`. Description of each key:
        - `"id_"` : `id` of svg `<path>` tag. It's required so each dict must contain `"id_"` key

        - `"from_"` : Direction from which a path should grow. Accepted values `"left"`, `"right"`, `"top"`, `"bottom"`, `"center_x"`(grow from center along horizontal axis), `"center_y"`, and `None`(Draw without animation). Defaults to `None`.

        - `"t"` : [Animation transition](https://kivy.org/doc/stable/api-kivy.animation.html?highlight=animation#kivy.animation.AnimationTransition). Defaults to `"out_sine"`.

        - `"d"` : Duration of animation. It'll still in-effect if `"from_"` is set to `None`. Defaults to .3

    - **on_complete**(optional) : Function to call after entire animation is finished. It can be used to create looping animation

    #### Important:
    - You must add a unique `id` to each path element you want to animate

    - Dict order in the list is important

* See [Demo code](https://raw.githubusercontent.com/shashi278/svg-anim-kivy/main/demo/main.py)
#

### Changelog

**v1.0**
* Shape animation feature added
* Added `anim_type` in draw method

**Earlier Changes**
* Added option to draw image without animation, `animate=False`
* Added option to draw empty or filled path, `fill=True` or `fill=False`

### Contribution

![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)

Whether you found a bug or have some idea to improve the project, PRs are always more than welcome

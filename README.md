## SVG-Anim-Kivy
*SVG path animation in kivy*

#

![Demo Gif](demo/svg_demo.gif)


#

### Requirement other than Kivy
* svg.path

### How to run demo?
**Note**: Demo code needs KivyMD to be installed. If you don't have(or don't want to install) kivymd then replace `MDIconButton` with your custom button and make sure to have a white background for widget because drawing color is black by default

* Clone it: `git clone https://github.com/shashi278/svg-anim-kivy.git`
* Change dir: `cd svg-anim-kivy`
* Install extra requirement: `pip install -r requirements.txt`
* Go to `src`: `cd src`
* Run it: `python demo.py`

### How to use?
*Easy and Straightforward*
```python
s = SVGAnimation(widget_to_draw_svg_upon)

# call animate method with a `svg_file` name
s.animate("github.svg")
```
#
#### PS: Try not to use very complex SVGs as they may degrade the performance

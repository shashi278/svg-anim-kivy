from setuptools import setup
import os, re

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version() -> str:
    """Get __version__ from version.py file."""
    from kivg import __version__ as version
    return version


setup(
    name="Kivg",
    version=get_version(),
    packages=["kivg"],
    package_data={"kivg": ["*.py", "animation/*.py", "drawing/*.py"]},
    # metadata to display on PyPI
    author="Shashi Ranjan",
    author_email="shashiranjankv@gmail.com",
    description="SVG path drawing and animation support in kivy application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="svg svg-animations svg-path svg-images kivy-application kivy python",
    url="https://github.com/shashi278/svg-anim-kivy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Android",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent"
    ],
    install_requires=["kivy>=2.0.0", "svg.path==4.1"],
    python_requires=">=3.6",
)
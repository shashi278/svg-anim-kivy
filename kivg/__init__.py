"""
Kivg - SVG drawing and animation for Kivy
"""
from kivy.logger import Logger
from .main import Kivg
from .version import __version__

_log_message = "Kivg:" + f" {__version__}" + f' (installed at "{__file__}")'
Logger.info(_log_message)

__all__ = ["Kivg"]

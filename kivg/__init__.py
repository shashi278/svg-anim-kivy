from kivy.logger import Logger
from .main import Kivg

__version__ = "1.0"
_log_message = "Kivg:" + f" {__version__}" + f' (installed at "{__file__}")'

Logger.info(_log_message)

from .constants import *
from .context import *
from .paths import *
from .plugins import *
from .postrender import *
from .presets import *
from .queue import *
from .render import *
from .ui import *

__author__ = "Brand New School, Dan Bradham"
__email__ = "dan@brandnewschool.com"
__license__ = "MIT"
__version__ = "0.1.5"
version_info = tuple([int(i) for i in __version__.split(".")])


def show_render_dialog():
    import c4d

    c4d.CallCommand(RENDER_COMMAND_ID)


def show_shotgrid_uploader_dialog():
    import c4d

    c4d.CallCommand(SHOTGRID_COMMAND_ID)

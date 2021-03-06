from .plugins import *
from .render import *
from .paths import *
from .constants import *
from .queue import *
from .context import *
from .presets import *
from .postrender import *
from .ui import *


__author__ = 'Brand New School, Dan Bradham'
__email__ = 'dan@brandnewschool.com'
__license__ = 'MIT'
__version__ = '0.1.2'
version_info = tuple([int(i) for i in __version__.split('.')])


def show_render_dialog():
    import c4d
    c4d.CallCommand(RENDER_COMMAND_ID)


def show_shotgrid_uploader_dialog():
    import c4d
    c4d.CallCommand(SHOTGRID_COMMAND_ID)

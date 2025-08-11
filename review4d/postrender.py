from .plugins import PluginType
from .queue import execute_in_main_thread

__all__ = [
    "PostRender",
    "get_post_renderer",
    "get_available_post_renderers",
    "get_post_renderers",
    "run_post_renderer",
]


class PostRender(PluginType):
    """PostRender plugins are run after a preview render completes.

    You could use a PostRender plugin to open the preview render in another
    program like djv or upload the render to ShotGrid.
    """

    enabled = False  # PostRender items will be unchecked in UI by default.
    _base_id = 30001

    def is_available(self):
        """Return True if this plugin is available for execution.

        You may want to check if certain resources are available. For example
        if you wanted to write an upload to ShotGrid after render plugin, this
        method may ensure that sgtk is importable.
        """

        return True

    def execute(self, render_path):
        """Implement this method to execute some code after a preview render
        finished."""

        return NotImplemented


def get_post_renderer(label_or_id):
    """Get a PostRender plugin by label or id."""

    return PostRender.get(label_or_id)


def get_post_renderers():
    """Get a list of all PostRender plugins."""

    return PostRender.list()


def get_available_post_renderers():
    """Get a list of all PostRender plugins."""

    return [pr for pr in PostRender.list() if pr().is_available()]


def run_post_renderer(label_or_id, render_path):
    """Execute a PostRender plugin."""

    post_renderer = get_post_renderer(label_or_id)()
    execute_in_main_thread(post_renderer.execute, render_path)

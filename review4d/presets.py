from . import paths
from .context import get_preview_name_from_context
from .plugins import PluginType, register_plugin

__all__ = [
    "get_path_preset",
    "get_path_presets",
    "get_preset_path",
    "PathPreset",
    "PathPresetError",
]


class PathPreset(PluginType):
    """PathPreset plugins are used to generate an output path for the review4d
    dialog. The ctx object contains valuable information about the active
    document and file path."""

    def execute(self, ctx):
        """Implement this method to return a file path for rendering."""

        return NotImplemented


class PathPresetError(Exception):
    """Raised by PathPreset subclasses to notify UI that preset failed to generate a path."""


def get_path_preset(preset_label_or_id):
    return PathPreset.get(preset_label_or_id)


def get_path_presets():
    """Get a list of all PathPreset plugins."""

    return PathPreset.list()


def get_preset_path(preset_label_or_id, file):
    """Execute a PathPreset plugin by label or id.

    Arguments:
        preset_label_or_id (str, int): PathPreset lookup like "Custom" or 100.
        file (str): Source file path to generate a new output file path from.

    Returns:
        str: Full path to output file for review.
    """

    preset = get_path_preset(preset_label_or_id)
    from . import context

    ctx = context.collect_context(file)
    return preset().execute(ctx)


class UserPreviewsPreset(PathPreset):
    label = "User Previews"
    order = 1

    def execute(self, ctx):
        preview_name = get_preview_name_from_context(ctx)
        preview_path = paths.normalize(
            paths.user_previews_path,
            preview_name,
        )
        return preview_path


class DesktopPreset(PathPreset):
    label = "Desktop"
    order = 2

    def execute(self, ctx):
        preview_name = get_preview_name_from_context(ctx)
        preview_path = paths.normalize(
            paths.desktop_path,
            preview_name,
        )
        return preview_path


class CustomPreset(PathPreset):
    label = "Custom"
    order = 100

    def execute(self, ctx):
        return None


# Register builtin plugins
register_plugin(UserPreviewsPreset)
register_plugin(DesktopPreset)
register_plugin(CustomPreset)

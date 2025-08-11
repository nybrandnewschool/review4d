import datetime

import review4d


class AnimPreset(review4d.PathPreset):
    """Generates a path to the correct review/animation folder in the
    BNS folder structure."""

    label = "Animation"
    order = -100

    def execute(self, ctx):
        preview_name = review4d.get_preview_name_from_context(ctx)
        preview_path = review4d.normalize(
            ctx["project_root"],
            "review/animation",
            ctx["folder"],
            ctx["parent"],
            ctx["name"],
            preview_name,
        )
        return preview_path


class DailiesPreset(review4d.PathPreset):
    """Generates a path to the correct dailies folder in the
    BNS folder structure."""

    label = "Dailies"
    order = -99

    def execute(self, ctx):
        preview_name = review4d.get_preview_name_from_context(ctx)
        preview_path = review4d.normalize(
            ctx["project_root"],
            "review/dailies",
            datetime.datetime.now().strftime("%Y-%m-%d"),
            preview_name,
        )
        return preview_path


def register():
    review4d.register_plugin(AnimPreset)
    review4d.register_plugin(DailiesPreset)

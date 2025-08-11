import os
import subprocess
import sys

import review4d


class ShowFile(review4d.PostRender):
    """Reveals the rendered file in the system file browser."""

    label = "Show in File Browser"
    enabled = False

    def is_available(self):
        return sys.platform in ["win32", "darwin", "linux2"]

    def execute(self, render_paths):
        if len(render_paths) == 1:
            file = render_paths[0]
            if sys.platform == "win32":
                subprocess.run(["explorer", "/select,", file.replace("/", "\\")])
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", file])
            else:
                subprocess.run(["xdg-open", os.path.dirname(file)])
        else:
            folders = set([os.path.dirname(path) for path in render_paths])
            for folder in folders:
                if sys.platform == "win32":
                    subprocess.run(["explorer", folder.replace("/", "\\")])
                elif sys.platform == "darwin":
                    subprocess.run(["open", "-R", folder])
                else:
                    subprocess.run(["xdg-open", os.path.dirname(folder)])


def register():
    review4d.register_plugin(ShowFile)

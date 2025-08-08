import sys
import subprocess

import review4d


class ShowFile(review4d.PostRender):
    '''Reveals the rendered file in the system file browser.'''

    label = 'Show in File Browser'
    enabled = False

    def is_available(self, options=None):
        return sys.platform in ['win32', 'darwin', 'linux2']

    def execute(self, render_path):
        if sys.platform == 'win32':
            subprocess.run(['explorer', '/select,', render_path.replace('/', '\\')])
        elif sys.platform == 'darwin':
            subprocess.run(['open', '-R', render_path])
        else:
            subprocess.run(['xdg-open', os.path.dirname(render_path)])


def register():
    review4d.register_plugin(ShowFile)

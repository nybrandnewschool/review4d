'''Builtin ContextCollector plugins.'''

import os
import re

from .plugins import PluginType, register_plugin
from . import paths

import c4d


__all__ = [
    'collect_context',
    'ContextCollector',
    'DefaultContextCollector',
    'get_context_collector',
    'get_context_collectors',
    'get_preview_name_from_context',
]


class ContextCollector(PluginType):
    '''ContextCollector plugins extract context from a file path.'''

    def execute(self, file, ctx):
        '''Implement this method to extend the ctx. This method should
        modify the ctx dict it receives and then return it.'''
        return NotImplemented


def get_context_collector(label_or_id):
    '''Get a ContextCollector plugin by label or id.'''

    return ContextCollector.get(label_or_id)


def get_context_collectors():
    '''Get a list of all PathPreset plugins.'''

    return ContextCollector.list()


def collect_context(file):
    '''Collect context from a file path.

    Executes all ContextCollector plugins on the given file path.

    Returns:
        dict containing keys and values extracted from the file path.
    '''

    ctx = {}
    for plugin in ContextCollector._registry:
        ctx = plugin().execute(file, ctx)

    return ctx


def get_preview_name_from_context(ctx):
    '''Use a context to generate a preview name.'''

    basename = ctx.get('basename')
    version = ctx.get('version')

    if basename and version:
        return f'{basename}_{version}.mp4'
    elif basename:
        return f'{basename}.mp4'
    else:
        return 'untitled.mp4'


class DefaultContextCollector(ContextCollector):
    '''Extracts context related to a file paths name.

    Example:

        {
            'file': '/project/anim_seq_010_v001.c4d',
            'c4d_project': '/project',
            'filename': 'anim_seq_010_v001.c4d'
            'basename': 'anim_seq_010',
            'version': 'v001',
            'ext': '.c4d'
        }
    '''

    version_pattern = r"v?\d+"

    def execute(self, file, ctx):

        if 'untitled' in file.lower():
            ctx.update({
                'file': file,
                'dirname': '',
                'filename': file,
                'basename': file.replace(' ', '_'),
                'version': '',
                'ext': '',
            })
            return ctx

        filename = os.path.basename(file)
        basename, ext = os.path.splitext(filename)

        versions = re.findall(self.version_pattern, basename)
        if versions:
            version = versions[-1]
            basename = basename.rsplit(version, 1)[0].rstrip('-_')
        else:
            version = ''

        ctx.update({
            'file': file,
            'dirname': os.path.dirname(file),
            'filename': filename,
            'basename': basename,
            'version': version,
            'ext': ext,
        })
        return ctx


# Register builtin plugins
register_plugin(DefaultContextCollector)

import importlib.util
import os


__all__ = [
    'PluginError',
    'PluginType',
    'register_plugin',
    'unregister_plugin',
    'load_plugins'
]


plugin_modules = []


class PluginType:
    '''Base class for all review4d Plugins. This class supports '''

    label = ''
    order = 0
    _base_id = 0
    _registry = None

    def __init_subclass__(cls):
        if cls._registry is None:
            cls._registry = []

    @classmethod
    def register(cls, plugin):

        if plugin in cls._registry:
            return

        plugin.id = max([p.id for p in cls._registry] + [cls._base_id]) + 1
        cls._registry.append(plugin)
        cls._registry.sort(key=lambda plugin: plugin.order)

    @classmethod
    def unregister(cls, plugin):
        if plugin in cls._registry:
            cls._registry.remove(plugin)

    @classmethod
    def get(cls, label_or_id):
        for plugin in cls._registry:
            if label_or_id in (plugin.id, plugin.label):
                return plugin

    @classmethod
    def list(cls):
        return list(cls._registry)

    def __str__(self):
        return '<{}:{}:{}>'.format(self.__class__.__name__, self.label, self.id)


class PluginError(Exception):
    '''Raised when a plugin fails to register or a plugin module fails to
    import.'''


def register_plugin(plugin):
    '''Register a plugin.'''

    if not issubclass(plugin, PluginType):
        raise PluginError((
            'Failed to register %s.'
            'Plugins must be a subclass of PathPreset or ContextCollector.'
        ) % plugin)

    plugin.register(plugin)


def unregister_plugin(plugin):
    '''Unregister a plugin.'''

    if not issubclass(plugin, PluginType):
        raise PluginError((
            'Failed to unregister %s.'
            'Plugins must be a subclass of '
            'PathPreset or ContextCollector.'
        ) % plugin)

    plugin.unregister(plugin)


def load_module(name, path):
    '''Load a python module by name and file path.'''

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_plugins():
    '''Load all plugins from REVIEW4D_PLUGINS paths.'''

    plugin_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'plugins')
    ]
    env_plugin_paths = os.getenv('REVIEW4D_PLUGINS')
    if env_plugin_paths:
        plugin_paths.extend(env_plugin_paths.split(os.pathsep))

    for path in plugin_paths:
        if not os.path.isdir(path):
            print('review4d> Plugin path not found: %s' % path)
            continue

        for file in os.listdir(path):
            if not file.endswith('.py'):
                continue

            module_path = os.path.join(path, file)
            module_name, _ = os.path.splitext(file)
            module = load_module(module_name, module_path)
            if hasattr(module, 'register'):
                module.register()

            plugin_modules.append(module)

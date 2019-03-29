"""
TODO: load() should be async
"""
from collections import OrderedDict
from os.path import join
from os import environ
import logging
from logging.handlers import WatchedFileHandler


class PipelineManagerBase():

    def __init__(self, label=None):
        self.started_count = 0
        self.lable = label
        self.step_dict = OrderedDict()
        self.receiver = None
        self._setup_logging()

    def add_step(self, plugin_instance_list, label=None):
        if label is None:
            label = "Step {}".format(len(self.step_dict) + 1)
        assert(label not in self.step_dict)

        plugin_dict = {}
        for plugin in plugin_instance_list:
            plugin_dict[plugin] = []

        self.step_dict[label] = plugin_dict

    def load(self):
        for step, plugins in self.all_steps:
            for plugin in plugins:
                control_manager, events_handler = plugin.load()
                plugins[plugin] = [control_manager, events_handler]

    def setup(self):
        for plugin in self.all_plugins:
            plugin.setup()

    @property
    def all_steps(self):
        for step, plugins in self.step_dict.items():
            yield step, plugins

    @property
    def all_plugins(self):
        for step, plugins in self.all_steps:
            for plugin in plugins:
                yield plugin

    @property
    def all_plugins_values(self):
        for step, plugins in self.all_steps:
            for value in plugins.values():
                assert(value)
                yield value

    @property
    def event_handlers(self):
        for plugin_values in self.all_plugins_values:
            _, event_handler = plugin_values
            yield event_handler

    @property
    def control_managers(self):
        for plugin_values in self.all_plugins_values:
            control_manager, _ = plugin_values
            yield control_manager

    def event_manager_to_plugin(self, event_manager):
        for step, plugins in self.step_dict.items():
            for plugin, values in plugins.items():
                control_manager, event_handler = values
                if event_handler == event_manager:
                    return plugin

    def event_controller(self, event_manager):
        for step, plugins in self.step_dict.items():
            for plugin, values in plugins.items():
                control_manager, event_handler = values
                if event_handler == event_manager:
                    return control_manager

    def control_manager(self, plugin):
        for step, plugins in self.all_steps:
            if plugin in plugins:
                control_manager, _ = plugins[plugin]
                return control_manager

    def remove_event_source(self, event_source):
        source_plugin = None
        for step, plugins in self.step_dict.items():
            for plugin, values in plugins.items():
                control_manager, event_handler = values
                if event_handler == event_source:
                    source_plugin = plugin
            if source_plugin:
                del self.step_dict[step][source_plugin]
                return
        raise Exception()

    def start(self):
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def loop(self):
        raise NotImplementedError

    def on_input(self, func):
        raise NotImplementedError

    def _setup_logging(self):
        loglevel = environ.get('LOG_LEVEL', 'INFO')
        logdir = environ.get('LOG_DIR')
        numeric_level = getattr(logging, loglevel.upper(), None)

        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        name = getattr(self, "instance_id", type(self).__name__)
        self.logger = logging.getLogger(name)

        if logdir:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fileName = join(logdir, name)+".log"
            fileHandler = WatchedFileHandler(fileName, mode='w')
            fileHandler.setFormatter(formatter)
            fileHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter('%(asctime)-15s {0} %(message)s'.format(name)))
        consoleHandler.setLevel(logging.INFO)
        self.logger.addHandler(consoleHandler)

        self.logger.setLevel(numeric_level)

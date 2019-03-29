from mdatapipe.engines.base.manager import PipelineManagerBase
from time import time
from os import environ


class PipelineManager(PipelineManagerBase):

    def loop(self):

        for plugin in self.all_plugins:
            if plugin.exit_code != 0:
                return plugin.exit_code, plugin.exit_msg

        return 0, "Finished"

    def setup(self):
        """ setup the resources required by the plugin instance """
        # The process needs to be started so that setup runs in the new pid
        for plugin in self.all_plugins:
            plugin.setup()

    def start(self):
        """ start all plugins """
        for plugin in self.all_plugins:
            plugin.start()

        # We send and item to the first plugin only
        first_step = list(self.all_steps)[0]
        for plugin in first_step[1]:
            plugin._on_input(time())

        # We must call exist to all plugins
        for plugin in self.all_plugins:
            plugin.exit()

        if __debug__:
            for plugin in self.all_plugins:
                print("%s stats:" % plugin.instance_id)
                if environ.get("MDP_PROFILE", False):
                    print(plugin._get_stats())
                else:
                    exit_msg = ''
                    for item in plugin._get_stats():
                        if 'clk_time' in item:
                            exit_msg += "\t %s: [Clk: %s] [CPU: %s] [#In: %d]" % (
                                item['label'], item['clk_time'], item['cpu_time'], item['count']
                                )
                        else:
                            exit_msg += " [#Out: %s]" % item['ocount']
                    print(exit_msg)

    def terminate(self):
        for plugin in self.all_plugins:
            plugin.exit()

    def connect(self, plugin1, plugin2, extra_label=''):
        if extra_label == '':
            plugin1.add_output_connection(plugin2, plugin2.instance_id)
        else:
            plugin1.add_extra_output_connection(extra_label, plugin2, plugin2.instance_id)

    def on_input(self, func):
        *_, last = self.all_steps   # Get the last step
        for plugin in last[1]:
            plugin.add_output_connection(self)
        self.on_input_func = func

    def _on_input(self, item):
        self.on_input_func(item)

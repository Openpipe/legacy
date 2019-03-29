"""
Description: Apply a Python's eval appended to an item and produce it
"""

from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self.exp_as_func = eval('lambda x: x' + self.config)

    def on_input(self, item):
        new_item = self.exp_as_func(item)
        self.put(new_item)

"""
Description: Produce an item for each element of a list provide in the config
"""
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        input_item = self.config or item
        for item in input_item:
            self.put(item)

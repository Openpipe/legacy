"""
Description: Split lines from input and produce each line
"""

from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        input_item = self.config or item
        for line in input_item.splitlines():
            self.put(line)

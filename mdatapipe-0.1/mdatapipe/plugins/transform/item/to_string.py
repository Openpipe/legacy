"""
Description: Split lines from input and produce each line
"""

from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        self.put(str(item))

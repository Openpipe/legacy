"""
Description: Produce a pretty printed item of the input item
"""
from mdatapipe.core import PipelinePlugin
from pprint import pformat


class Plugin(PipelinePlugin):

    def on_input(self, item):
        self.put(pformat(item))

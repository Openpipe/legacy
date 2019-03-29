"""
Description: Produce the yaml block provided in the config
"""

from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        self.put(self.config)

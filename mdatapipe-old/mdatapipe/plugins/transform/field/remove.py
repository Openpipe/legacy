"""
Description: Remove a field from an item
"""

from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_input(self, item):
        for key in self.config:
            del item[key]
        self.put(item)

"""
Description: Set field value
"""
from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_input(self, item):
        for key, value in self.config.items():
            item[key] = value
        self.put(item)

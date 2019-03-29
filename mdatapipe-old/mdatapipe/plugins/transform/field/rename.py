"""
Description: Rename field from an item
"""

from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_input(self, item):
        for old_name, new_name in self.config.items():
            value = item[old_name]
            del item[old_name]
            item[new_name] = value
        self.put(item)

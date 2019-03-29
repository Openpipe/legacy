"""
Description: Apply Python's Format() to field values
"""
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_input(self, item):
        for key, value in self.config.items():
            for key_item in key.split(','):
                key_item = key_item.strip()
                item[key_item] = value.format(item[key_item])
        self.put(item)

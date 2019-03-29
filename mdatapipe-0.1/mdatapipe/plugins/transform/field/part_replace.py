"""
Description: Replace words found in a value with other words
"""

from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_input(self, item):
        for field_name, replace_item in self.config.items():
            for replace_old, replace_new in replace_item.items():
                item[field_name] = item[field_name].replace(replace_old, replace_new)
        self.put(item)

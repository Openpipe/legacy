from mdatapipe.core import PipelinePlugin
"""
Description: Transform fields to integers
"""


class Plugin(PipelinePlugin):

    def on_start(self):
        for key_name in self.config.keys():
            if self.config.get(key_name, None) is None:
                self.config[key_name] = key_name

    def on_input(self, item):
        for source_field_name, target_field_name in self.config.items():
            current_value = item[source_field_name]
            item[target_field_name] = int(current_value)
        self.put(item)

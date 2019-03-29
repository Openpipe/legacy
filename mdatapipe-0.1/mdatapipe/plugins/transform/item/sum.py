from mdatapipe.core import PipelinePlugin
"""
Description: Generate the sum of values for fields
"""


class Plugin(PipelinePlugin):

    def on_start(self):
        self.sums = {}

    def on_input(self, item):
        for source_field_name, target_field_name in self.config.items():
            current_value = self.sums.get(target_field_name, 0)
            current_value += item[source_field_name]
            self.sums[target_field_name] = current_value

    def on_exit(self):
        new_dict = {}
        for target_field_name, sum_result in self.sums.items():
            new_dict[target_field_name] = sum_result
        self.put(new_dict)

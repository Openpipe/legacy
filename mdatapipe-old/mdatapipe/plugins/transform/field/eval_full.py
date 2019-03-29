"""
Description: Replace a field with the Python's eval(), the record fields are available as variables
"""
from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_input(self, item):
        for field_name, expr in self.config.items():
            item[field_name] = eval(expr, None, item)
        self.put(item)

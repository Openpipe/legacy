"""
Description: Replace a field with the Python's eval() of it's value appended with an expression
"""

from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_start(self):
        self.func_list = []
        for field_name, append_expr in self.config.items():
            exp_as_func = eval(('lambda x: x["%s"]' % field_name) + append_expr)
            self.func_list.append((field_name, exp_as_func))

    def on_input(self, item):
        for value in self.func_list:
            field_name, func = value
            item[field_name] = func(item)
        self.put(item)

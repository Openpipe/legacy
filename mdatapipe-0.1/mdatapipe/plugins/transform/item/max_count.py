from mdatapipe.core import PipelinePlugin
"""
Description: Limit the max number of items that are passed to the next plugin
"""


class Plugin(PipelinePlugin):

    def on_start(self):
        self.count = 0

    def on_input(self, item):
        max_count = int(self.config)
        if self.count < max_count:
            self.put(item)
            self.count += 1

"""
Description: Produce a copy of the new item unless an equal item was already produced

## Avoid duplicate entries
- filter using unique:
    input: $$
    max_items: 1000
"""

from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self.max_items = self.config.get('max_items', 0)
        self.unique_list = []

    def on_input(self, item):
        if item not in self.unique_list:
            if self.max_items and len(self.unique_list) == self.max_items:
                self.unique_list = []
            self.unique_list.append(item)
            self.put(item)

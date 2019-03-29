"""
Description: Produce the full text provided in the config
"""
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        if self.config is not None:
            text = str(self.config)
            for line in text.splitlines():
                self.put(line)
        else:
            text = str(item)
            self.put(text)

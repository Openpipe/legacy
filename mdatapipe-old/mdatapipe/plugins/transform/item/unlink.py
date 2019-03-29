"""
Description: Remove a file when an item is received
"""

from mdatapipe.core.plugin import PipelinePlugin
from os import unlink


class Plugin(PipelinePlugin):

    def on_input(self, item):
        path = self.config['path']
        try:
            unlink(path)
        except FileNotFoundError:
            if not self.config.get("ignore_errors"):
                raise
        self.put(item)

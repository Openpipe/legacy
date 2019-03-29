"""
Description: Sleep for the configured amount of time before producing a copy of the input item
"""
from time import sleep
from mdatapipe.core.plugin import PipelinePlugin
from mdatapipe.plugins.collect.datasource.clock import time2seconds


class Plugin(PipelinePlugin):

    def on_input(self, item):
        seconds = time2seconds(self.config)
        sleep(seconds)
        self.put(item)

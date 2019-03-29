"""
Description: Replace a date/time formatted value with an UTC timestamp
"""
from mdatapipe.core import PipelinePlugin
from datetime import datetime


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_input(self, item):
        for key, value in self.config.items():
            datetime_value = datetime.strptime(item[key], value)
            item[key] = datetime_value.timestamp()
        self.put(item)

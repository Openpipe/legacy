"""
Description: Replace words found in a value with other words
"""
from mdatapipe.core.plugin import PipelinePlugin
import re


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_start(self):
        # Ccompile regex on plugin start
        self.runtime_config = {}
        for field_name, regex in self.config.items():
            self.runtime_config[field_name] = re.compile(regex)

    def on_input(self, item):
        for field_name, regex in self.runtime_config.items():
            item[field_name] = regex.findall(item[field_name])[0]
        self.put(item)

"""
Description: Produce only the items whose value matches a regex expression
"""
from mdatapipe.core import PipelinePlugin
import re


class Plugin(PipelinePlugin):

    supported_types = [str]

    def on_start(self):
        include_list = self.config.get('include', [])
        exclude_list = self.config.get('exclude', [])
        self.include_list = []
        self.exclude_list = []
        for item in include_list:
            self.include_list.append(re.compile(item))
        for item in exclude_list:
            self.exclude_list.append(re.compile(item))

    def on_input(self, item):

        # Ignore items wich match an exclude regex
        for regex in self.exclude_list:
            if regex.match(item):
                return

        # If include list is empty, accept any item not excluded
        if len(self.include_list) == 0:
            self.put(item)
            return

        for regex in self.include_list:
            if regex.match(item):
                self.put(item)
                return

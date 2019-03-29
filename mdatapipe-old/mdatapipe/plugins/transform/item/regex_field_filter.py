"""
Description: Produce only the items whose value matches a regex expression
"""
from mdatapipe.core.plugin import PipelinePlugin
import re


class Plugin(PipelinePlugin):

    supported_types = [dict]

    def on_start(self):
        self.runtime_config = runtime_config = {}
        for field_name, rules in self.config.items():
            include_list = rules.get('include', [])
            exclude_list = rules.get('exclude', [])
            field_include_list = []
            field_exclude_list = []
            for item in include_list:
                field_include_list.append(re.compile(item))
            for item in exclude_list:
                field_exclude_list.append(re.compile(item))
            runtime_config[field_name] = (field_include_list, field_exclude_list)

    def on_input(self, item):
        exclude_item = False
        for field_name, rules in self.runtime_config.items():
            include_list, exclude_list = rules
            item_field_value = item[field_name]

            # Ignore items wich match an exclude regex
            for regex in exclude_list:
                if regex.match(item_field_value):
                    return

            # If include list is empty, accept any item not excluded
            if len(include_list) == 0:
                continue

            exclude_item = True
            for regex in include_list:
                    if regex.match(item_field_value):
                        exclude_item = False
                        break

            if not exclude_item:
                break

        if not exclude_item:
            self.put(item)

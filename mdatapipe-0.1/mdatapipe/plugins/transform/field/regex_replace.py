"""
Description: Search for a field matching and regex expression and replace it with a value
"""
import re
from mdatapipe.core import PipelinePlugin
from functools import partial
from collections import OrderedDict


class Plugin(PipelinePlugin):

    """:
    Plugin config is transformed to a more efficient runtime structure:
        runtime_config = { field_name: { match_pattern: replace_value ... } ...}
    """
    supported_types = [dict]

    def on_start(self):
        self.runtime_config = runtime_config = {}

        for field_name, replace_dict in self.config.items():
            field_dict = runtime_config.get(field_name, OrderedDict())
            runtime_config[field_name] = field_dict
            for pattern, replace_value in replace_dict.items():
                match_func = partial(re_match, re.compile(pattern))
                field_dict[match_func] = replace_value

    def on_input(self, item):
        for field_name, replace_dict in self.runtime_config.items():
            for match_func, replace_value in replace_dict.items():
                if match_func(item[field_name]):
                    item[field_name] = replace_value
        self.put(item)


def re_match(regex, value):
    return regex.match(value)

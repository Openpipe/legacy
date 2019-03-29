from mdatapipe.core.plugin import PipelinePlugin
from collections import OrderedDict


class Plugin(PipelinePlugin):

    """:
    Plugin config is transformed to a more efficient runtime structure:
        runtime_config = {
            field_name: {
                match_func: {
                    { match_value: new value }
                }
            }
        }
    """
    supported_types = [dict]

    def on_start(self):
        FUNC_MAP = {
            "": lambda x, y: x == y,
            "startswith": lambda x, y: x.startswith(y),
            "endswith": lambda x, y: x.endswith(y),
            "contains": lambda x, y: y in x,
            "in": lambda x, y: x in y,
        }
        self.runtime_config = runtime_config = {}
        for field_match, replace_dict in self.config.items():

            if ' ' in field_match:
                field_name, match_type = field_match.rsplit(' ', 1)
            else:
                field_name, match_type = field_match, ""

            match_funch = FUNC_MAP.get(match_type)

            # Update field name dict
            field_dict = runtime_config.get(field_name, OrderedDict())
            runtime_config[field_name] = field_dict

            # Update matching functions dict
            match_dict = field_dict.get(match_funch, OrderedDict())
            field_dict[match_funch] = match_dict

            # We must process the values from the shortest to the longest
            ordered_keys = sorted(replace_dict.keys(), key=lambda s: len(s), reverse=True)
            for match_value in ordered_keys:
                match_dict[match_value] = replace_dict[match_value]

    def on_input(self, item):
        for field_name, field_dict in self.runtime_config.items():
            for match_func, match_dict in field_dict.items():
                for match_value, replace_value in match_dict.items():
                    item_field_value = item[field_name]
                    if match_func(item_field_value, match_value):
                        item[field_name] = replace_value
                        break

        self.put(item)

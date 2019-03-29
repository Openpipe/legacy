"""
Plugins configuration can be dinamicaly updated with content available in the consumed items.
This module provides the dynamic configuration capabilities.

Examples:
    collect using tex: $doc$

    collect datasource file:
        path: $path$

    collect inline list:
        - $name$
        - $age$

    collect inline yaml:
        field: $name.lower()$

    $$ = replace with input item
    $name$ = replace with index 'name' from input item
    $name.x$ = replace with index 'name' appendded with .x $

"""
#  from mdatapipe import cloudpickle  # NOQA: F401
#  import dill as pickle  # NOQA: F401
from functools import partial
from copy import copy


def item_field(item, field_name, suffix=None):
    try:
        value = item[field_name]
    except TypeError:
        raise Exception("Expected an indexable item with field %s, got %s" % (field_name, item))
    return value


def item_field_attr(item, field_name, suffix):
    return getattr(item[field_name], suffix)


def item_field_index(item, field_name, suffix):
    return item[field_name][suffix]


class DynamicConfig(object):

    def __init__(self, config):
        """
        Build the metadata required to build a new config item with field names replace with input values

        :param config: the original object containing the config
        """
        self._original_config = config  # An original "template" maybe needed to rebuild the config
        self._full_item_config = False  # Config is $$, replace with item
        self._dynamic_config = {}       # Dict of fields with dynamic config

        if isinstance(config, str):
            if config == "$$":
                self._full_item_config = True
            else:
                self._update_dyna_config(config, '')

        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, str):
                    self._update_dyna_config(value, key)
                # When the item is a list, the watch stores (key_name, index)
                if isinstance(value, list):
                    for i in range(len(value)):
                        item = value[i]
                        self._update_dyna_config(item, (key, i))

    def _update_dyna_config(self, value, config_key):
        collected_string = ''
        conf_string_parts = []
        last_c = None
        collecting_literal = True

        if not isinstance(value, str):
            return

        #  Add fencing element to make sure the last value is collected
        value += '$'

        # Split fields on $, allowing to escape \$
        for c in value:
            if c == "$":
                if last_c == '\\':
                    collected_string = collected_string[:-1]  # Remove the trailing \
                else:
                    if collected_string:
                        if collecting_literal:
                            conf_string_parts.append(collected_string)
                        else:
                            conf_string_parts.append(self._string2func(collected_string))
                    collected_string = ''
                    collecting_literal = collecting_literal ^ True
                    continue
            collected_string += c
            last_c = c

        # Static literal ony
        if len(conf_string_parts) == 1 and isinstance(conf_string_parts[0], str):
            self._dynamic_config[config_key] = conf_string_parts[0]

        self._dynamic_config[config_key] = conf_string_parts

    def _string2func(self, conf_string):
        # Dynamic part
        dyna_func = partial(item_field, field_name=conf_string)
        if '.' in conf_string:
            field_name, field_suffix = conf_string.split('.', 1)
            dyna_func = partial(item_field_attr, field_name=field_name, suffix=field_suffix)
        if '[' in conf_string:
            field_name, field_suffix = conf_string.split('[', 1)
            field_suffix = field_suffix.strip("']")
            dyna_func = partial(item_field_index, field_name=field_name, suffix=field_suffix)
        return dyna_func

    def render(self, item):
        """
        :param item:    input item to be used for dynamic values
        :return:        config object, with dynamic items rendered based on the item
        """
        if self._full_item_config:
            return item

        if len(self._dynamic_config) == 0:
            return self._original_config

        config = copy(self._original_config)
        config_value = None
        for config_key, dyna_func_list in self._dynamic_config.items():

            config_value = ''
            for dyna_value in dyna_func_list:
                if callable(dyna_value):
                    new_value = dyna_value(item)
                    if config_value == '':
                        config_value = new_value
                    else:
                        config_value += str(new_value)
                else:
                    config_value += str(dyna_value)
                if config_key == '':
                    config = config_value
                else:
                    if isinstance(config_key, tuple):
                        key, index = config_key
                        config[key][index] = config_value
                    else:
                        config[config_key] = config_value

        return config
        # # Replaced all watched fields with item values
        # for watch_field, watch_list in self._watched_fields.items():
        #     if watch_field in item:
        #         for config_field in watch_list:
        #             config_key, func, field_suffix = config_field
        #             if isinstance(config_key, tuple):
        #                 key, index = config_key
        #                 config[key][index] = func(item[watch_field], field_suffix)
        #             else:
        #                 if watch_field:
        #                     if config_key:
        #                         config[config_key] = func(item[watch_field], field_suffix)
        #                     else:
        #                         # config_field is '', replace full config
        #                         config = func(item[watch_field], field_suffix)
        # return config

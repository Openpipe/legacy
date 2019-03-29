"""
Description: Sends items to a pipeline block
"""

from mdatapipe.core.plugin import PipelinePlugin
from collections import OrderedDict


class Plugin(PipelinePlugin):

    def on_load(self):
        self.pipeline_references = self.config.keys()
        self.selector = PipelineSelector(self.config)

    def on_input(self, item):
        for conn in self.selector.match(item):
            conn.send(item)

    def set_group_reference(self, name, connection):
        self.selector.set_group_reference(name, connection)

    def on_exit(self):
        for conn in self.selector.all_conns():
            conn.send(None)


class PipelineSelector:

    C_OR = 0
    C_AND = 1

    EVAL_MAP = {
        '>': lambda x, y: x > y,
        '<': lambda x, y: x < y,
        '<=': lambda x, y: x <= y,
        '>=': lambda x, y: x >= y,
        '==': lambda x, y: x == y,
    }

    def __init__(self, config):
        self._pipelines = {}
        for pipeline_name, conditions in config.items():
            # if conditions is None:
            self.append_conditions(pipeline_name, conditions)

    def all_conns(self):
        return self._pipelines.keys()

    def set_group_reference(self, name, connection):
        new_pipelines = OrderedDict()
        for block_name, steps in self._pipelines.items():
            if block_name == name:
                block_name = connection
            new_pipelines[block_name] = steps
        self._pipelines = new_pipelines

    def append_conditions(self, pipeline_name, conditions):
        self._pipelines[pipeline_name] = [[], []]
        if isinstance(conditions, dict):
            c_oper = self.C_OR
            condition_list = [conditions]
        elif isinstance(conditions, list):
            c_oper = self.C_AND
            condition_list = conditions
        elif conditions is None:
            return
        for condition in condition_list:
            for key, value in condition.items():
                compare_op = ''
                if not isinstance(value, int):
                    for char in value:
                        if char not in '><=':
                            break
                        compare_op += char
                    value = value[len(compare_op):]
                if compare_op == '':
                    compare_op = '=='
                eval_func = self.EVAL_MAP[compare_op]
                self._pipelines[pipeline_name][c_oper].append((key, eval_func, value))

    def item_type(self, item_value, value):
        if isinstance(item_value, int):
            value = int(value)
        return value

    def match(self, item):

        match_list = []

        for pipeline_name, cond_list in self._pipelines.items():

            # Loop AND conditions until getting a False
            skip_pipeline = False
            if cond_list[self.C_AND]:
                for cond_item in cond_list[self.C_AND]:
                    key, eval_func, value = cond_item
                    if key is None:
                        break
                    item_value = item[key]
                    value = self.item_type(item_value, value)
                    if not eval_func(item_value, value):
                        skip_pipeline = True
                        break

            if cond_list[self.C_OR]:
                skip_pipeline = True
                for cond_item in cond_list[self.C_OR]:
                    key, eval_func, value = cond_item
                    item_value = item[key]
                    value = self.item_type(item_value, value)
                    if eval_func(item_value, value):
                        skip_pipeline = False
                        break

            if not skip_pipeline:
                match_list.append(pipeline_name)
        return match_list

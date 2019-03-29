"""
Description: Produces a record from a text line parsing using regex group matching
"""

from mdatapipe.core.plugin import PipelinePlugin
import re
import sys


class Plugin(PipelinePlugin):

    def on_load(self):
        self._expr = re.compile(self.config['expr'])
        self._fields = self.config.get('fields', [])
        self._ignore_invalid = self.config.get('ignore_invalid', False)

    def on_input(self, item):
        item_dict = {}
        result = self._expr.findall(item)
        if result is None:
            if not self._ignore_invalid:
                print(self._expr, file=sys.stderr)
                raise Exception("Regex mismatch")
        result = result[0]

        expected_len = len(self._fields)
        result_len = len(result)
        if not result_len == expected_len:
            if not self._ignore_invalid:
                raise Exception("Regex mistmatch, expected %d fields, got %d !" % (expected_len, result_len))

        for i, field_name in enumerate(self._fields):
            conversion = None
            if ':' in field_name:
                field_name, conversion = field_name.split(':')

            if field_name[0] == "~":
                continue

            item_value = result[i]
            if conversion == "int":
                item_value = int(result[i])

            item_dict[field_name] = item_value
        self.put(item_dict)

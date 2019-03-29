"""
Description: Produces a record using GROK pattern matching from each received line
Requires: pygrok
"""
from mdatapipe.core.plugin import PipelinePlugin
from pygrok import Grok
import sys


class Plugin(PipelinePlugin):

    def on_load(self):
        expr = self.config['expr'].strip()
        ignore_invalid = self.config.get('ignore_invalid', False)
        self.mapper = GrokMapper(expr, ignore_invalid)

    def on_input(self, item):
        self.put(self.mapper.parse(item))


class GrokMapper:

    def __init__(self, expr, ignore_invalid=False):
        self.grok = Grok(expr)
        self.ignore_invalid = ignore_invalid

    def parse(self, line):
        result = self.grok.match(line)
        if result is not None:
            return result
        else:
            if not self.ignore_invalid:
                print(self.grok.pattern, file=sys.stderr)
                raise Exception("Grok mismatch")

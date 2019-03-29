from mdatapipe.core.plugin import PipelinePlugin
from mdatapipe.plugins.test.asserting.value import value_assert
from mdatapipe.plugins.test.asserting.value import Plugin as AssertPlugin


class Plugin(PipelinePlugin):

    supported_types = AssertPlugin.supported_types

    def on_start(self):
        self.check_index = 0

    def on_input(self, item):
        if self.check_index >= len(self.config):
            raise Exception("Test got more values than expected")
        value_assert(item, self.config[self.check_index])
        self.check_index += 1

    def on_exit(self):
        if self.check_index < len(self.config):
            raise Exception("Test less values than expected")

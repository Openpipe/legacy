from mdatapipe.core import PipelinePlugin
from mdatapipe.plugins.test.asserting.value import value_assert
from mdatapipe.plugins.test.asserting.value import Plugin as AssertPlugin


class Plugin(PipelinePlugin):

    supported_types = AssertPlugin.supported_types

    def on_start(self):
        self.check_index = 0

    def on_input(self, item):
        expected_count = len(self.config)
        value_assert(item, self.config[self.check_index])
        self.check_index += 1
        if self.check_index > expected_count:
            raise AssertionError("Test expected %d items, got %d" % (self.check_index, expected_count))

    def on_exit(self):
        if self.check_index < len(self.config):
            raise AssertionError("Test less values than expected")

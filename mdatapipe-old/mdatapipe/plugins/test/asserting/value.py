import sys
from mdatapipe.core.plugin import PipelinePlugin
from pprint import pprint


class Plugin(PipelinePlugin):

    supported_types = [dict, str, float, list]

    def on_input(self, item):
        value_assert(item, self.config)


def value_assert(item, assert_data):
    assert(len(assert_data) > 0)
    if isinstance(assert_data, dict):
        for key, value in assert_data.items():
            item_value = item.get(key)
            try:
                assert(item_value == value)
            except AssertionError:
                print(
                        "AssertionError: Expected %s on field '%s', got %s" %
                        (str(value), str(key), str(item_value)), file=sys.stderr
                    )
                raise
    else:
        try:
            assert(item == assert_data)
        except AssertionError:
            print("AssertionError: Expected %s, got %s" % (str(assert_data), str(item)), file=sys.stderr)
            raise
        else:
            pprint(item)

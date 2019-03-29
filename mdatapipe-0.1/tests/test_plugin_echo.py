from mdatapipe.core import PipelineManager
from mdatapipe.plugins.collect.inline.text import Plugin as TextPlugin
from mdatapipe.plugins.test.base.echo import Plugin as EchoPlugin


import sys

ASSERT_VALUE = "test123"


def test_plugin_echo():

    received_items = []

    def collect_result(item):
        received_items.append(item)

    manager = PipelineManager()
    text_plugin = TextPlugin("text-plugin", ASSERT_VALUE)
    echo_plugin = EchoPlugin("echo-plugin")
    manager.add_step([text_plugin])
    manager.add_step([echo_plugin])

    # Modules need to be loaded before we can setup connectors
    manager.load()
    manager.connect(text_plugin, echo_plugin)
    manager.on_input(collect_result)    # Must set on_input before singl thread start
    manager.start()

    exit_code, exit_message = manager.loop()
    if exit_code != 0:
        print("ERROR", exit_message, file=sys.stderr)

    assert(received_items[0] == ASSERT_VALUE)

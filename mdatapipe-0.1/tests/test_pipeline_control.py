from mdatapipe.core import PipelineManager
from mdatapipe.plugins.test.base.control import Plugin
import sys


def test_plugin_name():
    instance_id = Plugin("my-instance-id").instance_id
    assert(instance_id == "my-instance-id")


def test_pipeline_control():

    manager = PipelineManager()
    manager.add_step([Plugin("my-instance-id")])

    # Load plugins and setup the control/event connectors
    manager.load()

    # Start
    manager.start()

    exit_code, exit_message = manager.loop()
    if exit_code != 0:
        print("ERROR", exit_message, file=sys.stderr)

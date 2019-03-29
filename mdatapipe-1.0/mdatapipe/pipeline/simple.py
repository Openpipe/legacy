"""
    This file contains the implementation of the simple pipeline for the single-threaded-synchronous execution profile
    In order to keep it compatible with potential async implementations state changes management will be performed via
    callbacks.

    The loop() method is a fake loop that performs the load/start/run as synchronous by calling the corresponding
    callbaks
"""


class SimplePipeline(object):

    def __init__(self, data, filename):
        """
        Creates a simple pipeline object

        :param data:   The python object represting the YAML content of the pipeline
        :param data:   Optional filename to be used on error reporting details
        """
        self.data = data
        self.filename = filename
        self.on_success_cb = None
        self.on_failure_cb = None

    def load(self, on_success_cb, on_failure_cb):
        """
        """
        self.on_success_cb = on_success_cb
        self.on_failure_cb = on_failure_cb
        for step in self.data:
            if isinstance(step, dict):
                line_nr = step['__line__']
                items = list(step.items())
                if len(items) != 0:
                    raise ValueError(
                        "Pipeline step must be a dict with a single key. Got {} {}\n{}:{}".format(type(step), step,
                        self.filename, step['__line__'])
                    )
                component_name, component_config = step.items()[0]
            else:
                raise ValueError("Pipeline step must be a dict(). Got {} {}".format(type(step), step))
            print("Loading", component_name, component_config)

    def loop(self):
        """
        Fake loop, just execute the callbacks in order
        """
        self.on_success_cb()

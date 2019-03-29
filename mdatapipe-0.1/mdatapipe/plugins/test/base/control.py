from mdatapipe.core import PipelinePlugin
from os import getpid


class Plugin(PipelinePlugin):

    def on_start(self):
        print(self.instance_id, "ON_START", self, getpid())
        self.my_state = "start"

    def on_input(self, item):
        print(self.instance_id, "ON_INPUT", self, getpid())
        assert(self.my_state == "start")
        self.my_state = "got_item"

    def on_exit(self):
        print(self.instance_id, "ON_EXIT", self, getpid())
        assert(self.my_state == "got_item")
        self.my_state = "got_exit"

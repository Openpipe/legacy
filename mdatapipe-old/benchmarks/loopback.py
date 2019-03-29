# flake8: noqa
import sys
import os
from multiprocessing import Pipe

sys.path.append(os.getcwd())
from mdatapipe.core.plugin import PipelineBasePlugin 


class LoopbackPlugin(PipelineBasePlugin):

    def on_item(self):
        self.put(item)


plugin = LoopbackPlugin()
receiver, sender = Pipe(duplex=False)


def echo(sender, receiver, value):
    sender.send(value)
    response = receiver.recv()


people = {
    1: {'name': 'John', 'age': '27', 'sex': 'Male'},
    2: {'name': 'Marie', 'age': '22', 'sex': 'Female'},
    3: {'name': 'Luna', 'age': '24', 'sex': 'Female', 'married': 'No'}
}

%timeit echo(sender, receiver, "ok")


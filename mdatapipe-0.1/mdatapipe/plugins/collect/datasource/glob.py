"""
Description: Produce the list of files matching a glob pattern
"""
from os.path import expanduser
from glob import glob
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        intput_item = self.config.get("path", item)
        file_list = glob(expanduser(intput_item))
        if not file_list:
            raise Exception("No file found for " + str(intput_item))
        self.put(file_list)

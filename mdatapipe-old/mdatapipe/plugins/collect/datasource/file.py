"""
Description: Produce each line of a text file
"""
import gzip
import bz2
from os.path import expanduser, splitext
from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    ext_map = {
        '.gz': lambda x: gzip.open(x, 'rt'),
        '.bz': lambda x: bz2.open(x, 'rt'),
        '*': lambda x: open(x),
        }

    def on_input(self, item):
        input_item = expanduser(self.config.get('path', item))
        filename, file_extension = splitext(input_item)
        open_func = self.ext_map.get(file_extension, self.ext_map['*'])
        with open_func(input_item) as file:
            for line in file:
                line = line.strip("\r\n")
                self.put(line)
                self.refresh_status()

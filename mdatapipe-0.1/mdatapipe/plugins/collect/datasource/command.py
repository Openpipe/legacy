"""
Description: Executes a command and produce each line of it's output
"""

import os
import logging
from mdatapipe.core import PipelinePlugin
from subprocess import getstatusoutput


class Plugin(PipelinePlugin):

    def on_input(self, item):
        cmd = self.config['cmd']
        for env_item in self.config.get('env', []):
            items = env_item.items()
            for key, value in items:
                os.environ[key] = value
        status, output = getstatusoutput(cmd)
        if status != 0:
            logging.error(output)
            raise Exception("Error %d on command!" % status)
        for line in output.splitlines():
            self.put(line)

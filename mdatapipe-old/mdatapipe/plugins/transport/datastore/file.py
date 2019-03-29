"""
Description: Inserts an item into a file
"""

from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_first(self, item):
        path = self.config['path']
        mode = self.config.get('mode', 'w')
        self._file = open(path, mode)

    def on_input(self, item):
        msg = str(item)+"\n"
        self._file.write(msg)

    def on_exit(self):
        if hasattr(self, '_file'):
            self._file.close()

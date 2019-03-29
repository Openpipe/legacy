"""
Description: Inserts an item into a file
"""

from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        path = self.config['path']
        mode = self.config.get('mode', 'w')
        self.is_auto_close = self.config.get("auto_close", False)
        self._file = open(path, mode)

    def on_input(self, item):
        msg = str(item)+"\n"
        self._file.write(msg)
        if self.is_auto_close:
            self._file.close()

    def on_exit(self):
        if not self.is_auto_close:
            self._file.close()

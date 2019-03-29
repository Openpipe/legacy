#!/usr/bin/python
from os.path import realpath, commonprefix, join, isdir, isfile, getsize
from mdatapipe.core import PipelinePlugin
from mimetypes import guess_type


class Plugin(PipelinePlugin):

    def on_start(self):
        self._root_dir = self.config['root_dir']
        self._root_dir = realpath(self._root_dir)

    def on_input(self, item):
        relative_path = item['path'][1:]
        local_path = join(self._root_dir, relative_path)

        # Prevent directory traversal
        if commonprefix((realpath(local_path), self._root_dir)) != self._root_dir:
            return (404, {}, "Not found")

        # Search for an index file
        if isdir(local_path):
            local_path = join(local_path, "index.html")

        # Return file
        if not isfile(local_path):
            return (404, {}, "Not found")
        with open(local_path, 'r') as file:
            content = file.read()
        content_type, _ = guess_type(local_path)
        size = getsize(local_path)
        headers = {
            "Content-Type": content_type,
            "Content-Length": size
        }
        return (200, headers, content)

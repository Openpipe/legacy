#!/usr/bin/python
"""
Desc: Accetps http requests
"""
from mdatapipe.core import PipelinePlugin
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class Plugin(PipelinePlugin):

    def on_input(self, item):
        keep_running = True
        server_host = self.config.get('host', '')
        server_port = self.config.get('port', 8000)
        server_address = (server_host, server_port)
        self.MyHandler.set_owner(self)
        httpd = HTTPServer(server_address, self.MyHandler)
        httpd.timeout = 1
        while keep_running:
            httpd.handle_request()

    class MyHandler(BaseHTTPRequestHandler):
        owner = None

        @staticmethod
        def set_owner(owner):
            Plugin.MyHandler.owner = owner

        def do_GET(self):
            item = {}
            item['path'] = self.path
            http_status, headers, content = Plugin.MyHandler.owner.put(item, True)
            self.send_response(http_status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(content)

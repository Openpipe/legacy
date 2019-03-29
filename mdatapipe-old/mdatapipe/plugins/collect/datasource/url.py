"""
Description: Retrieves the content of an URL
"""

from mdatapipe.core.plugin import PipelinePlugin
import urllib.request as urlreq
from urllib.error import HTTPError


def lower(some_dict):
    new_dict = {}
    for key, value in some_dict.items():
        key = key.lower()
        new_dict[key] = value
    return new_dict


class Plugin(PipelinePlugin):

    def on_start(self):
        self.config['ua'] = self.config.get("ua", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")  # NOQA: E501
        self.config['timeout'] = self.config.get("timeout", 30)

    def on_input(self, item):
        url = self.config.get('path', item)
        timeout = self.config['timeout']
        req = urlreq.Request(url)
        req.add_header('User-Agent', self.config['ua'])
        try:
            reply = urlreq.urlopen(req, timeout=timeout)
        except HTTPError:
            if self.config.get('ignore_errors', False):
                return
            raise
        new_item = {}
        new_item['info'] = lower(dict(reply.info()))
        new_item['code'] = reply.getcode()
        new_item['url'] = reply.geturl()
        new_item['content'] = reply.read()
        self.put(new_item)

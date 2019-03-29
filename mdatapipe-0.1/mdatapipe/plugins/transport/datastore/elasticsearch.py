#!/usr/bin/python
"""
Description: Inserts an item into an ElasticSearch DB

    https://www.elastic.co/guide/en/elasticsearch/reference/6.3/docs-bulk.html


"""
import sys
import requests
from time import strftime
from json import dumps
from datetime import datetime
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self.buffer_size = self.config.get('buffer_size', 1)
        self.url = self.config.get('url', 'http://localhost:9200/')
        self.index = self.config.get('index', 'mdatapipe')
        self._url = self.url + "/_doc/_bulk"
        self.session = requests.Session()
        self.buffer = []

    def on_input(self, item):
        self.buffer.append(item)
        if len(self.buffer) == self.buffer_size:
            self.flush_buffer()

    def on_exit(self):
        self.flush_buffer()

    def flush_buffer(self):
        json_data = ''
        date_stamp = strftime("%Y-%m-%d")
        for item in self.buffer:
            json_data += '{"index": {"_index": "%s-%s", "_type": "_doc" }}\n' % (self.index, date_stamp)
            json_items = []
            for key, value in item.items():
                if isinstance(value, datetime):
                    value = str(value.date()) + "T" + str(value.time())
                json_items.append('"%s": %s' % (key, dumps(value)))
            json_data += '{%s}\n' % ', '.join(json_items)
        response = self.session.post(
            self._url, json_data,  headers={'Content-Type': 'application/x-ndjson'}
        )

        if not response.ok:
            print(json_data, file=sys.stderr)
            print(response.content, file=sys.stderr)
            response.raise_for_status()
            raise Exception("Unable to insert into elasticsearch")
        self.buffer = []

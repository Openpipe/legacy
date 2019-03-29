#!/usr/bin/python
"""
Description: Inserts an item into an ElasticSearch DB

    https://www.elastic.co/guide/en/elasticsearch/reference/6.3/docs-bulk.html


- output:
    - into:
        - elasticsearch:
            buffer_size: 1000
            index: datapipe
            url: http://localhost:9200/

"""
import sys
import requests
from time import strftime
from json import dumps
from datetime import datetime
from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self.config['buffer_size'] = self.config('buffer_size', 100)
        self.config['url'] = self.config('url', 'http://localhost:9200/')
        self.config['index'] = self.config('url', 'datapipe')

        self._url = self.config['url'] + "/_doc/_bulk"
        self.session = requests.Session()

    def on_input_buffer(self, buffer):
        date_stamp = strftime("%Y-%m-%d")
        for item in self.buffer:
            json_items = []
            for key, value in item.items():
                if isinstance(value, datetime):
                    value = str(value.date()) + "T" + str(value.time())
                if isinstance(value, str):
                    json_items.append('"%s": %s' % (key, dumps(value)))
                else:
                    json_items.append('"%s": %s' % (key, value))
            json_data = '{"index": {"_index": "%s-%s", "_type": "_doc" }}\n' % (self.config['index'], date_stamp)
            json_data += '{%s}\n' % ', '.join(json_items)
        response = self.session.post(
            self._url, json_data,  headers={'Content-Type': 'application/x-ndjson'}
        )
        if not response.ok:
            print(json_data, file=sys.stderr)
            print(response.content, file=sys.stderr)
            response.raise_for_status()
            raise Exception("Unable to insert into elasticsearch")

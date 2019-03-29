"""
Description: Inserts an item into an MongoDB database

- transport using mongodb:
    buffer_size: 100
    db: mdatapipe
    collection: my_table
    url: localhost:27017

Requires: pymongo
"""
from pymongo import MongoClient
from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self.config['buffer_size'] = self.get('buffer_size', 100)
        self.config['url'] = self.get('url', 'localhost:27017')
        self.config['db'] = self.get('db', 'mdatapipe')
        self.config['collection'] = self.get('collection', 'my_table')

        self.client = client = MongoClient('mongodb://%s/' % self.config['url'])
        db = client[self.config['db']]
        self._collection = db[self.config['collection']]

    def on_input_buffer(self, buffer):
        self._collection.insert(buffer)

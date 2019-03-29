"""
Description: Retrieves rows from an InfluxDB databse
"""

import sys
import requests
from datetime import datetime
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self.url = self.config.get('url', 'http://localhost:8086/')
        self.db_name = self.config.get('db_name', 'mdatapipe')
        self.session = requests.Session()

    def on_input(self, item):
        # https://docs.influxdata.com/influxdb/v1.6/guides/querying_data/
        query = self.config['query']
        url = "%squery?db=%s&q=%s" % (self.url, self.db_name, query)
        response = self.session.get(url)
        if not response.ok:
            print(response.content, file=sys.stderr)
            response.raise_for_status()
            raise Exception("Unable get data from influxdb")
        data = response.json()
        for result in data['results']:
            for serie in result.get('series', []):
                for item in serie['values']:
                    new_item = {}
                    new_item['measurement'] = serie['name']
                    for i in range(len(serie['columns'])):
                        col_name = serie['columns'][i]
                        new_item[col_name] = item[i]
                    record_time = new_item.get('time')
                    if record_time:
                        new_item['time'] = datetime.strptime(record_time, '%Y-%m-%dT%H:%M:%SZ')
                    self.put(new_item)

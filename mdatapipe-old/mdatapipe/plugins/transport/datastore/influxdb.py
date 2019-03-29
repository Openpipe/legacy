"""
Description: Inserts an item into an InfluxDB dataabase
"""

import sys
import requests
import pytz
from calendar import timegm
from datetime import datetime
from random import randint, seed
from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        seed()
        self.url = self.config.get('url', 'http://localhost:8086/')
        self.db_name = self.config.get('dbname', 'mdatapipe')
        self.session = requests.Session()
        self.tz = self.config.get('timestamp_zone', None)
        self.buffer_size = self.config.get('buffer_size', 1)
        if self.tz:
            self.timezone = pytz.timezone(self.tz)
        else:
            self.timezone = None
        self.counter = randint(0, 999)
        if self.config.get('timestamp_ms_count'):
            self.precision = 'ms'
        else:
            self.precision = self.config.get('precision', 's')
        self.data_lines = []

    def on_input(self, item):
        tag_set_list = []
        for tag_name in self.config.get('tag_set', ''):
            tag_set_list.append("%s=%s" % (tag_name, item[tag_name]))
        tag_set = ','.join(tag_set_list)
        field_set_list = []
        skip_line = False
        for field_name in self.config['field_set']:
            field_value = item.get(field_name, None)
            # Skip lines with values set to None
            # if field_value is None:
            #    skip_line = True
            #    break
            field_set_list.append("%s=%s" % (field_name, field_value))
        if skip_line:
            return
        field_set = ','.join(field_set_list)
        timestamp = self.utc_timestamp(item)
        if tag_set:
            tag_set = ',' + tag_set
        data = "%s%s %s %s" % (self.config['measurement'], tag_set, field_set, timestamp)
        self.data_lines.append(data)
        if len(self.data_lines) == self.buffer_size:
            self.flush_buffer()

    def flush_buffer(self):
        if len(self.data_lines) == 0:
            return

        url = "%swrite?db=%s&precision=%s" % (self.url, self.db_name, self.precision)
        data = '\n'.join(self.data_lines)
        response = self.session.post(
            url, data,  headers={'Content-Type': 'application/octet-stream'}
        )
        if not response.ok:
            print(response.content, file=sys.stderr)
            response.raise_for_status()
            raise Exception("Unable to insert into influxdb")
        self.data_lines = []

    def utc_timestamp(self, item):
        timestamp_field = self.config.get('timestamp')
        if not timestamp_field:
            return ''
        timestamp = item.get(timestamp_field, '')
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, self.config['timestamp_format'])
            if self.timezone:
                local_timestamp = self.timezone.localize(timestamp)
                timestamp = local_timestamp.astimezone(pytz.UTC)
            timestamp = timestamp.strftime("%s")
            if self.config.get('timestamp_ms_count'):
                ms = "%03d" % self.counter
                timestamp += ms
                self.counter += 1
                if self.counter > 999:
                    self.counter = 0
            return timestamp
        if isinstance(timestamp, datetime):
            timestamp = timegm(timestamp.utctimetuple())
        return timestamp

    def on_exit(self):
        self.flush_buffer()

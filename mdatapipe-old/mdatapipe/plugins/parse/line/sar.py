"""
Description: Produces records from Linux's SAR output parsing

This plugin receives a single sar output line.
When an end of section (empty line) is found
it outputs a sar metric in the JSON format

The SarDataParser was adapted from:
    https://github.com/joaompinto/sar2es/blob/master/sar2es.py

The input data must be obtained with a format similar to:
    TZ=UTC LC_TIME=C LANG=C sar -pA 1 1
"""
from mdatapipe.core.plugin import PipelinePlugin
from datetime import datetime
import re
import sys


class Plugin(PipelinePlugin):

    supported_types = [str]

    def on_load(self):
        self.parser = SarDataParser()

    def on_input(self, item):
        parse_result = self.parser.process(item)
        if parse_result:
            for result in parse_result:
                self.put(result)


class SarDataParser:

    def __init__(self):
        self.metrics_info = None
        self.metrics_header = None
        self.metrics_data = []
        self.all_data = []
        self.json = ''

    def _sar2json(self):
        json_record_list = []
        if self.metrics_header is not None:
            # Process the data that was retrieved
            if len(self.metrics_data) == 1:
                metric_name = 'system'
                base_index = 1
            else:
                metric_name = self.metrics_header[1]
                base_index = 2
            # Ignore this type of data
            if self.metrics_header[1] in ["INTR", "BUS", "FAN", "TEMP"]:
                self.metrics_header = None
                self.metrics_data = []
                return None
            metric_name = metric_name.lower()
            for metric_record in self.metrics_data:
                date = self.metrics_info[0][3]
                timestamp_str = date+" "+metric_record[0]
                timestamp = re.sub('/', '-', timestamp_str)
                timestamp = datetime.strptime(timestamp, "%m-%d-%y %H:%M:%S")
                if metric_name == "system":
                    component = "system"
                else:
                    component = metric_record[1]
                for i in range(base_index, len(self.metrics_header)):
                    json_record = {
                        'hostname': self.metrics_info[0][2],
                        'component': component,
                        'metric_name': metric_name,
                        'metric_category': self.metrics_header[i],
                        'value': float(metric_record[i].replace(',', '.')),
                        'timestamp': timestamp,
                    }
                    json_record_list.append(json_record)
        self.metrics_header = None
        self.metrics_data = []
        return json_record_list

    def process(self, line):
        if line == "":  # Reached an end of section,
            return self._sar2json()
        if line.startswith("Average") or line[0] == "#":
            return None
        if self.metrics_info is None:
            sar_re = r"(\S+)\s+(\S+)\s+\(([\w\.]+)\)\s+(\S+)"
            self.metrics_info = re.findall(sar_re, line)
            if not self.metrics_info:
                print("HEADER:", line, file=sys.stderr)
                print("REGEX", sar_re, file=sys.stderr)
                raise Exception("SAR header does not match regex")
        elif self.metrics_header is None:
            self.metrics_header = line.split()
        else:
            self.metrics_data.append(line.split())
        return None

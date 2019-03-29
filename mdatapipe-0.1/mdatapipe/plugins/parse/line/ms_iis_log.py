"""
Description: Produces a record from a Microsoft IIS log line parsing
"""
from mdatapipe.core import PipelinePlugin
from datetime import datetime


class Plugin(PipelinePlugin):

    def on_start(self):
        self.field_list = []

    def on_input(self, item):
        item = item.lower()
        if item[0] == '#':
            # Comment line
            if item.startswith('#fields:'):  # Field structure
                self.field_list = item.split(":", 1)[1].split()
        else:
            # Data line
            log_line_fields = item.split(" ")
            log_line_dict = {}
            for i in range(len(self.field_list)):
                field_name = self.field_list[i]
                field_value = log_line_fields[i]
                log_line_dict[field_name] = field_value
            timestamp_str = log_line_dict['date'] + " " + log_line_dict['time']
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            del log_line_dict['date']
            del log_line_dict['time']
            log_line_dict['timestamp'] = timestamp
            self.put(log_line_dict)

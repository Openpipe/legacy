"""
Description: Produces records from NMON's output parsing

"""
from mdatapipe.core import PipelinePlugin
from datetime import datetime


class Plugin(PipelinePlugin):

    supported_types = [str]

    def on_start(self):
        self.parser = NMONDataParser()

    def on_input(self, item):
        parse_result = self.parser.process(item)
        if parse_result is not None:
            self.put(parse_result)


class NMONDataParser:

    IGNORE_RECORDS = ["BBBP", "UARG", "TOP", "JFSFILE"]

    def __init__(self):
        self.dt_timestamp = None
        self.hostname = None
        self.last_record_type = None
        self.metric_headers = {}

    def process(self, line):
        fields = line.split(',')
        record_type = fields[0]
        if record_type in self.IGNORE_RECORDS:
            return None
        if record_type == 'AAA':
            if fields[1].lower() == 'host':
                self.hostname = fields[2]
            return None
        if record_type == 'ZZZZ':
            self.save_time(fields)
            return None
        return self.produce_record(fields)

    def save_time(self, fields):
        timestamp = fields[2] + " " + fields[3]
        self.dt_timestamp = datetime.strptime(timestamp, '%H:%M:%S %d-%b-%Y')

    def produce_record(self, fields):
        record_type, description, fields = fields[0], fields[1], fields[2:]

        if self.metric_headers.get(record_type):
            _, field_names = self.metric_headers[record_type]
        else:  # If a record type is found for the first time, it's a header
            self.metric_headers[record_type] = (description, fields)
            return None

        record = {"metric_name": record_type,  "timestamp": self.dt_timestamp}
        record["hostname"] = self.hostname
        record['components'] = {}

        for i, field_name in enumerate(field_names):
            if not field_name:  # Some record types contain a trailing empty comma
                continue
            if fields[i] == '':  # Skip void values
                continue
            try:
                value = float(fields[i])
            except ValueError:
                value = fields[i]
            record['components'][field_name] = value

        return record

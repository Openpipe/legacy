#!/usr/bin/python
"""
Description: Produce a CSV line from an item
"""
import csv
import io
from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_start(self):
        self.is_first_run = True
        self.include_header = self.config.get('include_header', False)

    def on_input(self, item):
        if self.is_first_run:
            self.is_first_run = False
            if self.include_header:
                self.put(self.csv2string(item.keys()))
        self.put(self.csv2string(item.values()))

    def csv2string(self, data):
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(data)
        return si.getvalue().strip('\r\n')

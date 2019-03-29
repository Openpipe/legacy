"""
Description: Produces a record from each received CSV line
"""
from mdatapipe.core import PipelinePlugin
import sys
import csv


class Plugin(PipelinePlugin):

    supported_types = [str]

    def on_start(self):
        self.delimiter = self.config.get("delimiter", ',')
        self.quotechar = self.config.get("quotechar", '"')
        self.field_list = self.config.get("field_list", [])
        self.is_auto_number = self.config.get("auto_number", False)
        ignore_errors = self.config.get('ignore_errors', False)
        if self.field_list:
            self.mapper = CSVMapper(self.field_list, self.delimiter, self.quotechar, ignore_errors)

    def on_input(self, item):

        # No field list defined, and getting first entry
        if not self.field_list:
            self.field_list = item.split(self.delimiter)
            self.mapper = CSVMapper(self.field_list, self.delimiter, self.quotechar)
        else:
            new_item = self.mapper.parse(item)
            if new_item:
                if self.is_auto_number:
                    for key, value in new_item.items():
                        try:
                            new_item[key] = float(value)
                        except ValueError:
                            pass
                self.put(new_item)


class CSVMapper:

    def __init__(self, field_list, delimiter=',', quotechar='"', ignore_errors=False):
        self.delimiter, self.quotechar = delimiter, quotechar
        self.build_field_groups(field_list)
        self.ignore_errors = ignore_errors

    def build_field_groups(self, field_list):
        """
        Create a field group for each item in the list, when ":count" is not provided, use 1
        A field group is a tuple (field_name, field_count), csv values will be mapped to fields
        based in the field group definition
        """
        self.field_list = []
        self.field_count = 0

        for counter, value in enumerate(field_list):
            if ':' in value:
                field_name, field_count = value.split(':')
                field_count = int(field_count)
            else:
                field_name, field_count = value, 1
            field_name = field_name.strip()
            field_group = field_name, field_count
            self.field_list.append(field_group)
            self.field_count += field_count

    def parse(self, line):
        reader = csv.reader([line], delimiter=self.delimiter, quotechar=self.quotechar)
        row = [x for x in reader][0]
        if self.field_count != len(row):
            if self.ignore_errors:
                return
            print("FIELD_LIST",  self.field_list, file=sys.stderr)
            raise Exception("Expected %d elements, got %d" % (self.field_count, len(row)))
        new_item = {}
        field_index = 0
        for field_group in self.field_list:
            field_name, field_count = field_group
            if field_name[0] != '~':
                if field_name[0] == '%':
                    field_name = field_name[1:]
                    try:
                        new_item[field_name] = int(row[field_index])
                    except ValueError:
                        if self.ignore_errors:
                            return
                        else:
                            raise
                else:
                    field_group = row[field_index:field_index+field_count]
                    new_item[field_name] = self.delimiter.join(field_group)
            field_index += field_count
        return new_item

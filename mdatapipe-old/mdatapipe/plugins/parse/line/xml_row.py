"""
Description: Produces a record for each XML element found matching a search criteria
"""

from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_load(self):
        element = None
        if self.config:
            element = self.config.get('element', None)
        if element is None:
            element = "row"
            self._element = '<' + element + ' '

    def on_input(self, value):

        line_dict = {}
        value = value.strip()

        if not value.startswith(self._element):
            return
        value += '0="0"'  # append a sentinel value
        line_i = 4

        while line_i < len(value):
            field_name = ''
            while value[line_i] == " ":
                line_i += 1
            char = value[line_i]

            while char != "=":
                if char != ' ':
                    field_name += char
                line_i += 1
                char = value[line_i]

            if field_name[0] == '/':    # end xml with followed by a sentinelq
                self.put(line_dict)
                return

            line_i += 2
            close_quote = value.find('"', line_i)
            fied_value = (value[line_i:close_quote])
            line_dict[field_name] = fied_value
            line_i = close_quote + 1

from mdatapipe.core import PipelinePlugin
from lxml import html

"""
Requires: lxml
"""


class Plugin(PipelinePlugin):

    def on_input(self, item):
        mux_to_dict = self.config.get('target')
        input_item = self.config.get('input', item)
        dom = html.fromstring(input_item)
        for link in dom.xpath(self.config['xpath']):
            link = str(link)
            if mux_to_dict:
                item[mux_to_dict] = link
                self.put(item)
            else:
                self.put(link)

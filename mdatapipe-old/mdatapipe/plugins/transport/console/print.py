from mdatapipe.core.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        item = self.config or item
        print(item)

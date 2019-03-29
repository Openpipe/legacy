"""
Description: Sends items to pipeline segments
"""

from mdatapipe.core import PipelinePlugin


class Plugin(PipelinePlugin):

    pass

    #  def on_start(self):
    #    self.pipeline_references = self.config.keys()
    # This is currently handled at pipeline.py becuse the info needs to be available before_start

    def on_input(self, item):
        pass  # This is a transport, we don't need to do nothing

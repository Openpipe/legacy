"""
    DPL Component Skeleton Class

    Details on the features anf interfaces of components are available at:
        https://github.com/mdatapipe/mdatapipe-1.0/blob/master/docs/DatapipePipelineLanguageV1.adoc

    A component in a simple, single-threaded pipeline provides the following channels:
        - input
        - output
        - error
"""


class Component:

    def __init__(self):
        self.input_channel = None
        self.output_channel = None
        self.error_channel = None

    def set_channnels(self, input_channel, output_channel, error_channel):
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.error_channel = error_channel

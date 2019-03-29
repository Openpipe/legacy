"""
This example demonstrates how to build and run a pipeline from a python script
"""
from mdatapipe.core.pipeline import PipelineBase
from mdatapipe.plugins.collect.using.file import Plugin as FilePlugin
from mdatapipe.plugins.parse.using.xml_row import Plugin as XmlRowPlugin

pipeline = PipelineBase(save_results=True)

pipeline.add_step([FilePlugin({'path': '/tmp/academia/PostHistory.xml.gz'})])
pipeline.add_step([XmlRowPlugin()])

pipeline.start()
pipeline.wait_end()


for item in pipeline.result_data:
    print("RESULT", item)

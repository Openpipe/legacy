from mdatapipe.core.engine import select_component

PipelineManager = select_component("manager")
PipelinePlugin = select_component("plugin")

__all__ = ["PipelineManager", "PipelinePlugin"]

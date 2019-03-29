from .yaml import load_yaml, remove_line_info


class PipelineDocument(object):

    def __init__(self, yaml_data, filename):
        self.yaml_data = yaml_data
        self.filename = filename

    def load(self, on_step_cb=None):
        """
        """
        pipeline_data = load_yaml(self.yaml_data, self.filename)

        # _pipeline will be set to either a SimplePipeline or StructuredPipeline based on the data schema
        if isinstance(pipeline_data, list):    # Simple pipeline
            pass  # self._pipeline = SimplePipeline(pipeline_data, filename)
        elif isinstance(pipeline_data, dict):    # Simple structured
            pass  # self._pipeline = StructuredPipeline(pipeline_data, filename)
        else:
            raise ValueError("""
            The top level YAML element on file {} must be of type list or dict.
            Got {}
            """.format(self.filename, type(self.filename)))

        for step in self.data:
            if isinstance(step, dict):
                line_nr = step['__line__']
                remove_line_info(step)
                items = list(step.items())
                if len(items) != 0:
                    raise ValueError(
                        "Pipeline step must be a dict with a single key. Got {} {}\n{}:{}"
                        .format(type(step), step, self.filename, step['__line__'])
                    )
                component_name, component_config = step.items()[0]
            else:
                raise ValueError("Pipeline step must be a dict(). Got {} {}".format(type(step), step))
            print("Loading", component_name, component_config)

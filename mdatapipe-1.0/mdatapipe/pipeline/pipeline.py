from ..dpl import PipelineDocument, load_component
from time import now


class PipelineManager(object):

    def __init__(self, filename=None, data=None):
        """
        :param filename:    The name of the file with the pipeline YAML
        :param data:        The YAML content as a string
        """
        self.step_list = []  # List of steps from the pipeline
        # add_step_cb() will be called during document loading ation every time a step is found
        self.dpl_doc = PipelineDocument(filename, data, self.add_step_cb)

    def add_step_cb(self, step_name, step_config):
        """ Create a single instance of a component and add it to the step_list """
        comp_instance = load_component(step_name, step_config)
        self.step_list.append(comp_instance)

    def create_links(self):
        """ Output link is a memory reference to the next component """
        for i, step in enumerate(self.step_list[:-1]):
            step.output_link = step[i+1]

    def start(self):
        for step in self.step_list:
            on_start_func = getattr(step, 'on_start', None)
            if on_start_func:
                on_start_func()

    def activate(self):
        self.steps[0]._on_input(now())  # Send current time to the firs step to activate it
        self.steps[0]._on_input(None)   # Send end-of-input «None» to trigger the on_finnish() execution
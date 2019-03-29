"""
The PipeLine class extends the PipelineBaseclass with YAML / plugin import capabilities
"""
import requests
import sys
from re import findall, MULTILINE
from yaml import Loader
from yaml.composer import Composer
from yaml.constructor import Constructor
from fnmatch import fnmatch
from os.path import join
from mdatapipe.client.colorhelper import info
from importlib import import_module
from mdatapipe.core import PipelineManager


class PipelineInfo:

    def __init__(self, data=None, file=None, parallel=None):
        # If data is None read data datasource file
        if data is None:
            with open(file, 'r') as data_file:
                data = data_file.read()

        # Load YAML text data into a python object
        self.pipeline_text = data
        self.pipeline_data = load_yaml(data)
        self.pipeline_references = {}

        self._load_plugins()

    def _load_plugins(self):
        """
        Load and init all pipeline plugins as declared in the pipeline description
        """
        self.requires = []
        if not isinstance(self.pipeline_data, list):
            raise Exception("Expecting list element, got " + str(self.pipeline_data))
        for step in self.pipeline_data:
            if not isinstance(step, dict):
                raise Exception("Expecting key mapping, got " + str(step))
            plugin_name, plugin_config = list([x for x in step.items() if x[0] != "__line__"])[0]
            try:
                op_group, op_type, op_driver = plugin_name.split(" ")
            except ValueError:
                raise Exception("Plugin name must contain 3 components, got: "+str(plugin_name))
            module_name = join(op_group, op_type, op_driver+".py")
            full_module_name = join('mdatapipe', 'plugins', module_name)
            with open(full_module_name) as module_file:
                module_source = module_file.read()
            requires = findall(r'^\W*Requires:\W*(.*)', module_source, MULTILINE)
            self.requires.extend([x.strip() for x in requires])  # Remove surroundng space


class FilePipeline:

    def __init__(self, data=None, file=None, parallel=None, silent=False):
        """ Load data pipeline definition datasource file """
        self.file = file
        self._plugin_config_list = []  # List of config to be applied to plugins
        self.silent = silent
        self.manager = PipelineManager()
        self.blocks = {}

        # If data is None read data datasource file
        if data is None:
            if file.startswith('http:') or file.startswith('https:'):
                r = requests.get(file, allow_redirects=True)
                data = r.text
            else:
                with open(file, 'r') as data_file:
                    data = data_file.read()

        # Load YAML text data into a python object
        self.pipeline_text = data
        self.pipeline_data = load_yaml(data)

        # Parse parallel control arguments
        self.parallel_rules = self._parse_rules(parallel)

        # Load all plugins
        self._load_plugins()

    def add_step(self, block_name, step):
        block_steps = self.blocks.get(block_name, [])
        block_steps.append(step)
        self.blocks[block_name] = block_steps

    def _handle_step(self, block_name, op_group, op_type, op_driver, op_config, line_nr):
        if op_group == "config" and op_type == "for" and op_driver == "modules":
            for config_item in op_config:
                self._plugin_config_list.append(config_item)
        else:
            self._load_plugin(block_name, op_group, op_type, op_driver, op_config, line_nr)

    def _load_block(self, block_name, block_data):
        if block_data is None:
            raise Exception("Block segement %s is empty!" % block_name)
        for step in block_data:
            if not isinstance(step, dict):
                raise Exception("Expecting key mapping, got " + str(step))
            plugin_name, plugin_config = list([x for x in step.items() if x[0] != "__line__"])[0]
            line_nr = step['__line__']
            try:
                op_group, op_type, op_driver = plugin_name.split(" ")
            except ValueError:
                raise Exception("Plugin name must contain 3 components, got: "+str(plugin_name))
            self._handle_step(block_name, op_group, op_type, op_driver, plugin_config, line_nr)

    def _load_block_references(self):
        # Check for references to other blocks, and "load" them
        processed_list = []
        while len(processed_list) == 0 or len(self.blocks) > len(processed_list):
            # Prevent OrderedDict mutated during iteration
            blocks_copy = self.blocks.copy()
            for block_name, steps in blocks_copy.items():
                if block_name in processed_list:
                    continue
                processed_list.append(block_name)
                for step in steps:
                    for process in step:
                        pipeline_list = getattr(process, "pipeline_references", [])
                        for pipeline_name in pipeline_list:
                            if pipeline_name not in self.blocks:
                                try:
                                    block_data = self.pipeline_data[pipeline_name]
                                except KeyError:
                                    raise(Exception("Unable to find pipeline with name " + pipeline_name))
                                    exit(6)
                                self._load_block(pipeline_name, block_data)

    def _load_plugins(self):
        """
        Load and init all pipeline plugins as declared in the pipeline description
        """
        try:
            start_block = self.pipeline_data['start']
        except (KeyError, TypeError):
            print("Datapipe file must have a 'start:' block", file=sys.stderr)
            exit(5)
        self._load_block('start', start_block)
        self._load_block_references()

    def _load_plugin(self, block_name, op_group, op_type, op_driver, op_config, line_nr):
        """ Init a plugin associated with a step """
        self._delete_line_info(op_config)
        step_processes = []
        module_name = join(op_group, op_type, op_driver+".py")
        full_module_name = join('mdatapipe', 'plugins', module_name)
        process_count = self.parallel_rules.get(full_module_name, 1)
        desc = module_name + ":" + str(line_nr)
        if line_nr > 0:
            prev_line = self.pipeline_text.splitlines()[line_nr-2]
            if len(prev_line) > 3 and prev_line[0:2] == "##":
                desc = prev_line[3:]

        if not self.silent:
            print('{:>50} , {} proc(s)'.format(info(desc), info(process_count)))

        for process_nr in range(process_count):
            module_name = '_'.join([op_group, op_type, op_driver])
            process_name = module_name + "_" + str(line_nr) + "_" + str(process_nr)

            # Apply global config matching plugin name
            for config_item in self._plugin_config_list:
                if fnmatch(module_name, config_item['name']):
                    if op_config:
                        op_config.update(config_item['set'])
                    else:
                        op_config = config_item['set']
            plugin = load_plugin_module(op_group, op_type, op_driver, op_config, process_name)
            plugin.execution_id = "%s:%s[%s]" % (self.file, line_nr, full_module_name)
            plugin.name = process_name
            plugin.desc = desc
            step_processes.append(plugin)

            # TODO: Move this to a proper place
            if op_driver == "send_to":
                plugin.pipeline_references = op_config.keys()

        self.manager.add_step(step_processes)
        self.add_step(block_name, step_processes)

    def _delete_line_info(self, op_config):
        if op_config and isinstance(op_config, dict):
            try:
                del op_config["__line__"]
            except KeyError:
                pass
            for key, value in op_config.items():
                self._delete_line_info(value)
        if op_config and isinstance(op_config, list):
            for value in op_config:
                self._delete_line_info(value)

    def _parse_rules(self, rules_list):
        if rules_list is None:
            return {}

        rules_dict = {}

        for rule in rules_list:
            plugin_name, value = rule.split(':')
            rules_dict[plugin_name] = int(value)
        return rules_dict

    def printTable(self, tbl, borderHorizontal='-', borderVertical='|', borderCross='+'):
        cols = [list(x) for x in zip(*tbl)]
        lengths = [max(map(len, map(str, col))) for col in cols]
        f = borderVertical + borderVertical.join(' {:>%d} ' % l for l in lengths) + borderVertical
        s = borderCross + borderCross.join(borderHorizontal * (l+2) for l in lengths) + borderCross

        print(s)
        for row in tbl:
            print(f.format(*row))
            print(s)

    def start(self):
        self.manager.load()
        self.setup_connections()
        self.setup_segment_connections()
        self.manager.start()

    def wait_end(self):
        exit_code, exit_message = self.manager.loop()
        return exit_code, exit_message

    def setup_connections(self):
        for block_steps in self.blocks.values():
            for i in range(len(block_steps) - 1):
                current_step = block_steps[i]
                next_step = block_steps[i+1]
                for current_instance in current_step:
                    for next_instance in next_step:
                        self.manager.connect(current_instance, next_instance)

    def setup_segment_connections(self):

        # Setup links to reference segments
        for block_name, block_steps in self.blocks.items():
            for current_step in block_steps:
                for current_process in current_step:
                    references = getattr(current_process, 'pipeline_references', [])
                    for ref_name in references:
                        target_reference = self.blocks[ref_name]
                        for target_plugin in target_reference[0]:
                            self.manager.connect(current_process, target_plugin, ref_name)


def load_yaml(data):
    """
    Load YAML data extending it with line number information, nodes get a __line__ attribute
    """
    loader = Loader(data)

    def compose_node(parent, index):
        # the line number where the previous token has ended (plus empty lines)
        line = loader.line
        node = Composer.compose_node(loader, parent, index)
        node.__line__ = line + 1
        return node

    def construct_mapping(node, deep=False):
        mapping = Constructor.construct_mapping(loader, node, deep=deep)
        mapping['__line__'] = node.__line__
        return mapping
    loader.compose_node = compose_node
    loader.construct_mapping = construct_mapping
    data = loader.get_single_data()
    return data


def load_plugin_module(op_group, op_type, op_driver, op_config, process_name):
    """ Load a plugin module """
    # script_dir = dirname(abspath(__file__))
    module_name = join(op_group, op_type, op_driver+".py")
    module_sys_name = '.'.join(['mdatapipe', 'plugins', op_group, op_type, op_driver])
    # module_fname = join(script_dir, 'plugins', module_name)
    try:
        module = import_module(module_sys_name)
    except ImportError as error:
        print(error, file=sys.stderr)
        raise Exception("Unable to import module %s" % module_name)

    if not hasattr(module, 'Plugin'):
        raise Exception("Plugin module '%s' does not provide a Plugin class!" % module_sys_name)
    return module.Plugin(process_name, op_config)

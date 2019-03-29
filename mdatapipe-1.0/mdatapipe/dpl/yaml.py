"""
This file provides a YAML loader function wich augments nodes with the liner number information.
"""
import sys
from yaml import Loader
from yaml.composer import Composer
from yaml.constructor import Constructor
from yaml.parser import ParserError


def load_yaml(yaml_data, filename):
    """
    Load YAML data extending it with line number information, nodes get a __line__ attribute
    """
    if yaml_data is None:
        with open(filename, 'r') as data_file:
            yaml_data = data_file.read()

    loader = Loader(yaml_data)

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
    try:
        python_data = loader.get_single_data()
    except ParserError as error:
        print("YAML syntax error parsing file {} :".format(filename), file=sys.stderr)
        print(error, file=sys.stderr)
        exit(1)
    return python_data


def remove_line_info(self, yaml_data):
    if yaml_data and isinstance(yaml_data, dict):
        try:
            del yaml_data["__line__"]
        except KeyError:
            pass
        for key, value in yaml_data.items():
            remove_line_info(value)
    if yaml_data and isinstance(yaml_data, list):
        for value in yaml_data:
            remove_line_info(value)

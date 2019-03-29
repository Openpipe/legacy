from importlib import import_module
from os.path import join
import sys


def load_plugin_module(op_group, op_type, op_driver, op_config):
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
    return module.Plugin(op_config, module_name)

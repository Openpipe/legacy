from os import environ
from importlib import import_module


MDP_ENGINE = environ.get("MDP_ENGINE", "singlethread")


def select_component(name):
    MAP = {
        "manager": "PipelineManager",
        "plugin": "PipelinePlugin",
    }
    component_class = MAP.get(name)
    engine_mod_path = '.'.join(["mdatapipe", "engines", MDP_ENGINE, name])
    module = import_module(engine_mod_path)
    return getattr(module, component_class)

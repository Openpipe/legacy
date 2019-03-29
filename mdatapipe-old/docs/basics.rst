Basics
------

Data Pipeline
#############
A data pipeline is composed by a sequence of steps, typically starting with a "collect" step and ending with an "output" step.
Data pipelines are described using `YAML <https://en.wikipedia.org/wiki/YAML>`_ files. A step is an instance of a `PipelinePlugin`. A plugin always wait for input dat «they do not consume CPU when idle» and produce new data and or outputs data to an external resource.

A step is defined by 3 levels of nested lists.

The following example representes a single step that loads the "collect/from/file" plugin, with the configuration { path: '/var/log/sa/sar*' } :

.. literalinclude:: basics.yaml
    :language: yaml
    :lines: 1-5

The next steps receives the full content from the file, and outputs lines:

.. literalinclude:: basics.yaml
    :language: yaml
    :lines: 6-

When no output step is provided, mdatapipe automatically appends the `prettyprint` plugin, which calls `pprint()` for each result tha tis received.

Pipeline Plugin
###############
A plugin is a python module which provides a `Plugin` class derived from `PipelinePlugin`.

This is the code for the plugin, when an item is received, it's split into lines, and lines are pushed to the input of the next plugin.

.. literalinclude:: ../mdatapipe/plugins/parse/how/splitlines.py
    :language: python

You can check the list/source of all the `Plugins <https://github.com/mdatapipe/mdatapipe/tree/master/mdatapipe/plugins>`_ distributed with mdatapipe.




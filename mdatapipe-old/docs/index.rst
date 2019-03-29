mdatapipe - multiprocess plugin-driven data pipeline engine
===========================================================

.. toctree::
    :hidden:

    intro.rst
    install.rst
    basics.rst


`mdatapipe <http://www.mdatapipe.org>`_ is a multiprocess plugin-driven data pipeline engine,
it can be used for data collection, analysis and reporting.

mdatapipe allows users to create data processing pipelines using simple declarative configuration
files. Each step in a pipeline is handled by a plugin, plugins are executed in isolated processes,
steps can be parallelized to maximize throughput on multi-core systems.

mdatapipe is in a planning phase of development, currently the entire pipeline runs
in a single system, but in the future it should possible to run "distributed" pipelines, using
containers and cloud resources.

A data pipeline typically looks like this:

.. literalinclude:: datapipe.yaml
    :language: yaml



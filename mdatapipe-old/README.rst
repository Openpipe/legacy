mdatapipe
=========

|pypi version| |GitHub Forks| |GitHub Open Issues| |travis-ci for master
branch| |coverage report for master branch| |sphinx documentation for
latest release|

Requirements
------------

-  Python 3.6+ (currently tested with 3.6)

Installation
------------

.. code:: bash

    pip install mdatapipe

Examples
--------

.. code:: bash

    mdatapipe run pipeline.yaml

Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the `GitHub
Issue Tracker <https://github.com/mdatapipe/mdatapipe/issues>`__. Pull
requests are welcome. Issues that don't have an accompanying pull
request will be worked on as my time and priority allows.

Guidelines
----------

Testing
-------

Testing is done via `pytest <http://pytest.org/latest/>`__, driven by
`tox <http://tox.testrun.org/>`__.

Testing is as simple as:

.. code:: bash

    pip install tox
    tox

Release Checklist
-----------------

.. |pypi version| image:: https://img.shields.io/pypi/v/mdatapipe.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/mdatapipe
.. |GitHub Forks| image:: https://img.shields.io/github/forks/mdatapipe/mdatapipe.svg
   :target: https://github.com/mdatapipe/mdatapipe/network
.. |GitHub Open Issues| image:: https://img.shields.io/github/issues/mdatapipe/mdatapipe.svg
   :target: https://github.com/mdatapipe/mdatapipe/issues
.. |travis-ci for master branch| image:: https://secure.travis-ci.org/mdatapipe/mdatapipe.png?branch=master
   :target: http://travis-ci.org/mdatapipe/mdatapipe
.. |coverage report for master branch| image:: https://codecov.io/github/mdatapipe/mdatapipe/coverage.svg?branch=master
   :target: https://codecov.io/github/mdatapipe/mdatapipe?branch=master
.. |sphinx documentation for latest release| image:: https://readthedocs.org/projects/mdatapipe/badge/?version=latest
   :target: https://readthedocs.org/projects/mdatapipe/?badge=latest

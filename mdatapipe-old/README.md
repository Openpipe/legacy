mdatapipe
=========

[![pypi version](https://img.shields.io/pypi/v/mdatapipe.svg?maxAge=2592000)](https://pypi.python.org/pypi/mdatapipe)
[![GitHub Forks](https://img.shields.io/github/forks/mdatapipe/mdatapipe.svg)](https://github.com/mdatapipe/mdatapipe/network)
[![GitHub Open Issues](https://img.shields.io/github/issues/mdatapipe/mdatapipe.svg)](https://github.com/mdatapipe/mdatapipe/issues)
[![travis-ci for master branch](https://secure.travis-ci.org/mdatapipe/mdatapipe.png?branch=master)](http://travis-ci.org/mdatapipe/mdatapipe)
[![coverage report for master branch](https://codecov.io/github/mdatapipe/mdatapipe/coverage.svg?branch=master)](https://codecov.io/github/mdatapipe/mdatapipe?branch=master)
[![sphinx documentation for latest release](https://readthedocs.org/projects/mdatapipe/badge/?version=latest)](https://readthedocs.org/projects/mdatapipe/?badge=latest)

Requirements
------------

- Python 3.6+ (currently tested with 2.7, 3.6)

Installation
------------

To install the development version:
``` {.sourceCode .bash}
pip install mdatapipe
```

To install the latest released version:
``` {.sourceCode .bash}
pip install https://github.com/mdatapipe/mdatapipe/archive/master.zip
```

Examples
--------

```bash
mdatapipe run pipeline.yaml
```

Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the [GitHub
Issue
Tracker](https://github.com/mdatapipe/mdatapipe/issues).
Pull requests are welcome. Issues that don't have an accompanying pull
request will be worked on as my time and priority allows.

Guidelines
----------

Testing
-------

Testing is done via [pytest](http://pytest.org/latest/), driven by
[tox](http://tox.testrun.org/).

Testing is as simple as:

```bash
pip install tox
tox
```

Release Checklist
-----------------

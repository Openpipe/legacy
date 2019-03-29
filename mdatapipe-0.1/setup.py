#!/usr/bin/env python
"""Install using distutils

Run:
    python setup.py install

to install this package.
"""
from setuptools import setup, find_packages
from os.path import join
from glob import glob

with open('requirements.txt') as r_file:
    requirements = r_file.read()

with open('README.rst') as r_file:
    long_desc = r_file.read()

name = "mdatapipe"

setup(
    name=name,
    version=open(join(name, 'version')).readline().strip("\r\n"),
    long_description=long_desc,
    install_requires=[x for x in requirements.splitlines() if x],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    data_files=[(join('share', 'mdatapipe', 'examples'), glob(join('examples', '*')))],
    entry_points='''
        [console_scripts]
        mdatapipe=mdatapipe.client.__main__:main
        '''
)

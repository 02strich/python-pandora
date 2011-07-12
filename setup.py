#!/usr/bin/env python
from setuptools import setup
from pandora import DATA_FILES

setup(name='python-pandora',
    version='0.4-31',
    description='Library to access pandora.com. Based on the work from http://forum.xbmc.org/showthread.php?t=70471',
    maintainer='Stefan Richter',
    maintainer_email='stefan@02strich.de',
    packages = ['pandora'],
    data_files = [('pandora', ['pandora/'+file for file in DATA_FILES])],
    #install_requires=['Flask >= 1.0'],
)
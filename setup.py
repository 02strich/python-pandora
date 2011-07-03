#!/usr/bin/env python
from setuptools import setup

setup(name='python-pandora',
    version='0.3',
    description='Library to access pandora.com. Based on the work from http://forum.xbmc.org/showthread.php?t=70471',
    maintainer='Stefan Richter',
    maintainer_email='stefan@02strich.de',
    packages = ['pandora'],
    data_files = [('pandora', ['pandora/crypt_key_input.h', 'pandora/crypt_key_output.h'])],
    #install_requires=['Flask >= 1.0'],
)
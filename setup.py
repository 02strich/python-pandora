#!/usr/bin/env python
from setuptools import setup

setup(name='python-pandora',
      version='0.9',
      description='Library to access pandora.com. Based on the work from http://forum.xbmc.org/showthread.php?t=70471 and from Pithos',
      maintainer='Stefan Richter',
      maintainer_email='stefan@02strich.de',
      packages=['pandora'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.1',
      ],
      use_2to3=True,
      )

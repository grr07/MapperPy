#!/usr/bin/env python

from distutils.core import setup

setup(name='MapperPy',
      version='0.11.1py34',
      description='Automatic object mapping tool',
      author='Lukasz Grech',
      author_email='mapperpy@gmail.com',
      url='https://github.com/lgrech/MapperPy',
      packages=['mapperpy'],
      install_requires=['enum34'],
      tests_require=['assertpy'],
      keywords='object mapping')

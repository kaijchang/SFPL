#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import os

setup(
    name='sfpl',
    packages=['sfpl'],
    version='1.5.1',
    description='Unofficial Python API for SFPL',
    author='Kai Chang',
    author_email='kaijchang@gmail.com',
    url='https://github.com/kajchang/sfpl-scraper',
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'README.md')).read(),
    install_requires=[open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'requirements.txt')).read().split('\n')[:-1]],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)

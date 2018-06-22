from setuptools import setup
import os

setup(
    name='sfpl',
    packages=['sfpl'],
    version='1.1.5',
    description='Python Scraper for SFPL Website',
    author='Kai Chang',
    url='https://github.com/kajchang/sfpl-scraper',
    license='MIT',
    long_description=open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'README.md')).read(),
    long_description_content_type="text/markdown",
    install_requires=['robobrowser'])

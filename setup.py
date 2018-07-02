from setuptools import setup
import os

setup(
    name='sfpl',
    packages=['sfpl'],
    version='1.1.14',
    description='Unofficial Python API for SFPL',
    author='Kai Chang',
    author_email='kaijchang@gmail.com',
    url='https://github.com/kajchang/sfpl-scraper',
    license='MIT',
    long_description=open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'README.md')).read(),
    long_description_content_type="text/markdown",
    install_requires=['beautifulsoup4==4.6.0', 'requests==2.19.1'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)

import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as readme:
    long_description = readme.read()

with open(os.path.join(here, "requirements.txt")) as requirements:
    install_requires = requirements.read().split("\n")[:-1]

setup(
    name="sfpl",
    packages=["sfpl"],
    version="1.6.1",
    description="Unofficial Python API for SFPL",
    author="Kai Chang",
    author_email="kaijchang@gmail.com",
    url="https://github.com/kajchang/sfpl-scraper",
    license="MIT",
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=install_requires,
    entry_points={"console_scripts": ["sfpl=sfpl.cli:main"]},
)

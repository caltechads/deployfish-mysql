#!/usr/bin/env python
from deployfish_mysql import __version__
from setuptools import setup, find_packages


setup(
    name="deployfish-mysql",
    version=__version__,
    description="Deployinator MySQL plugin",
    author="Caltech IMSS ADS",
    author_email="imss-ads-staff@caltech.edu",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click >= 6.7",
        "deployfish >= 0.14.5",
        "shellescape == 3.4.1"
    ],
    entry_points={'deployfish.command.plugins': [
        'mysql = deployfish_mysql.mysql'
    ]},
)

#!/usr/bin/env python
from deployfish_mysql import __version__
from setuptools import setup, find_packages


setup(
    name="deployfish-mysql",
    version=__version__,
    description="Deployfish MySQL plugin",
    author="Caltech IMSS ADS",
    author_email="imss-ads-staff@caltech.edu",
    url="https://github.com/caltechads/deployfish-mysql",
    keywords=['aws', 'ecs', 'docker', 'devops', 'mysql'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click >= 6.7",
        "deployfish >= 0.22.0",
        "shellescape == 3.4.1"
    ],
    entry_points={'deployfish.command.plugins': [
        'mysql = deployfish_mysql.mysql'
    ]},
)

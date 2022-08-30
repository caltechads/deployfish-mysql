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
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "cement >= 3.0",
        "click >= 7.0",
        "deployfish > 1.7.4"
    ],
    entry_points={
        'deployfish.plugins': ['mysql = deployfish_mysql']
    },
)

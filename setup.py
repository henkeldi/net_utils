# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='net_utils',
    version='0.0.1',
    description='Helper functions for DeepLearning frameworks',
    author='Dimitri Henkel',
    author_email='Dimitri.Henkel@gmail.com',
   	package_data={'net_utils': ['shader/*']},
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs'))
)
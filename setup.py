#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'techies'
]

with open('requirements.txt') as f:
    requires = f.read().strip().splitlines()

with open('LICENSE') as f:
    license = f.read().strip()

with open('README.rst') as f:
    readme = f.read().strip()

with open('CHANGES.rst') as f:
    changes = f.read().strip()

long_description = readme + '\n\n' + changes

setup(
    name='techies',
    version='0.1.0',
    description='Opinionated Python toolbox',
    long_description=long_description,
    author='Runzhou Li (Leo)',
    author_email='runzhou.li@gmail.com',
    url='https://github.com/woozyking/techies',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'techies': 'techies'},
    include_package_data=True,
    install_requires=requires,
    license=license,
    zip_safe=False,
    classifiers=(
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
    ),
)

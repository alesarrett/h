# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import re
from codecs import open
from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as _test

###############################################################################

NAME = 'memex'
DESC = 'Memex: annotation storage and retrieval'
AUTHOR = 'Hypothes.is Project & contributors'
AUTHOR_EMAIL = 'contact@hypothes.is'
URL = 'https://h.readthedocs.io'
LICENSE = 'Simplified (2-Clause) BSD License'
KEYWORDS = ['annotation', 'storage', 'hosting']
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Framework :: Pyramid',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
]
INSTALL_REQUIRES = [
    'SQLAlchemy>=0.8.0',
    'annotator>=0.14.2,<0.15',
    'elasticsearch>=1.1.0,<2.0.0',
    'jsonschema>=2.5.1,<2.6',
    'psycopg2>=2.6.1,<2.7',
    'pyramid>=1.6,<1.7',
    'python-dateutil>=2.1',
]
EXTRAS_REQUIRE = {}
ENTRY_POINTS = {}

with open('README.rst', encoding='utf-8') as fp:
    LONGDESC = fp.read()

###############################################################################

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(HERE, 'src', 'memex', '__init__.py')


def get_version():
    """Extract package __version__"""
    with open(VERSION_FILE, encoding='utf-8') as fp:
        content = fp.read()
    match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Could not extract package __version__")


class test(_test):
    def run(self):
        print('please run tox instead')


if __name__ == "__main__":
    setup(name=NAME,
          version=get_version(),
          description=DESC,
          long_description=LONGDESC,
          classifiers=CLASSIFIERS,
          keywords=KEYWORDS,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          license=LICENSE,
          install_requires=INSTALL_REQUIRES,
          extras_require=EXTRAS_REQUIRE,
          entry_points=ENTRY_POINTS,
          cmdclass={'test': test},
          packages=find_packages(where='src'),
          package_dir={'': 'src'},
          zip_safe=False)

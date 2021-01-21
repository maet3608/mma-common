#!/usr/bin/env python

import io
import shutil
import subprocess
import sys
from glob import glob
from os.path import isfile

from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand

import mmacommon


def read_readmes(*filenames, **kwargs):
    """Read readme files."""
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for folder in ['build']:
            if isfile(folder):
                shutil.rmtree(folder)
        """Remove egg-info folder."""
        for info_file in glob('*egg-info'):
            shutil.rmtree(info_file)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


class PyLintCommand(TestCommand):
    user_options = []

    def finalize_options(self):
        pass

    def run(self):
        subprocess.call(['pylint', 'mmacommon'])


setup(
    name=mmacommon.__name__,
    version=mmacommon.__version__,
    url='git@github.com:maet3608/mma-common.git',
    author='Stefan Maetschke',
    author_email='stefan.maetschke@gmail.com',
    description='Common library for Multimedia Analytics',
    long_description=read_readmes('README.md'),
    packages=find_packages(exclude=['setup']),
    install_requires=[
        'six>= 1.10.0',
        'numpy>=1.11.0',
        'Pillow>=7.1.0',
        'scikit-image>=0.12.3',

    ],
    tests_require=['pytest'],
    zip_safe=False,
    platforms='any',
    cmdclass={
        'lint': PyLintCommand,
        'test': PyTest,
        'clean': CleanCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

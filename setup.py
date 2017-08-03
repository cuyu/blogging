#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
from src import __VERSION__
from setuptools.command.install import install
import os


def enable_argcomplete():
    with open(os.path.join(os.path.expanduser("~"), '.zshrc'), 'w') as f:
        f.write('eval "$(register-python-argcomplete blogging)"\n')


class CustomInstallCommand(install):
    """Customized setuptools install command"""

    def run(self):
        install.run(self)
        enable_argcomplete()


setuptools.setup(
    name='github-blogging',
    version=__VERSION__,
    description='A cmdline tool to help managing your blogs',
    packages=['src'],
    author='Curtis Yu',
    author_email='icyarm@icloud.com',
    install_requires=[
        'argcomplete',
        'tabulate'
    ],
    url='https://github.com/cuyu/blogging',
    entry_points={
        "console_scripts": [
            "blogging = src.blogging:main",
        ],
    },
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2'
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
)

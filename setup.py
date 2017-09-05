#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
from blogging.constants import __VERSION__
from setuptools.command.install import install
import os
import subprocess


def find_default_shell():
    cmd = 'echo $SHELL'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdout = proc.stdout.readline()
    return os.path.basename(stdout.strip())


def write_if_not_exist(path, line):
    exist = False
    with open(path, 'r') as f:
        l = f.readline()
        while l:
            if l == line:
                exist = True
            l = f.readline()
    if not exist:
        with open(path, 'a') as f:
            f.write(line)


def enable_argcomplete():
    default_shell = find_default_shell()
    write_if_not_exist(os.path.join(os.path.expanduser("~"), '.{0}rc'.format(default_shell)),
                       '\neval "$(register-python-argcomplete blogging)"\n')


class CustomInstallCommand(install):
    """Customized setuptools install command"""

    def run(self):
        install.run(self)
        enable_argcomplete()


setuptools.setup(
    name='github-blogging',
    version=__VERSION__,
    description='A cmdline tool to help managing your blogs',
    packages=['blogging'],
    author='Curtis Yu',
    author_email='icyarm@icloud.com',
    install_requires=[
        'argcomplete',
        'tabulate',
        'termcolor',
    ],
    url='https://github.com/cuyu/blogging',
    entry_points={
        "console_scripts": [
            "blogging = blogging.blogging:main",
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

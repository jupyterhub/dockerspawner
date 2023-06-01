#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# -----------------------------------------------------------------------------
# Minimal Python version sanity check (from IPython/Jupyterhub)
# -----------------------------------------------------------------------------
from __future__ import print_function

import os
import sys

if os.name in ('nt', 'dos'):
    error = "ERROR: Windows is not supported"
    print(error, file=sys.stderr)

# At least we're on the python version we need, move on.

from setuptools import setup

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

install_requires = []
with open('requirements.txt') as f:
    for line in f.readlines():
        req = line.strip()
        if not req or req.startswith('#'):
            continue
        install_requires.append(req)

from setuptools.command.bdist_egg import bdist_egg


class bdist_egg_disabled(bdist_egg):
    """Disabled version of bdist_egg

    Prevents setup.py install from performing setuptools' default easy_install,
    which it should never ever do.
    """

    def run(self):
        sys.exit(
            "Aborting implicit building of eggs. Use `pip install .` to install from source."
        )


setup_args = dict(
    name='dockerspawner',
    packages=['dockerspawner'],
    version="12.2.0.dev",
    description="""Dockerspawner: A custom spawner for Jupyterhub.""",
    long_description="Spawn single-user servers with Docker.",
    author="Jupyter Development Team",
    author_email="jupyter@googlegroups.com",
    url="https://jupyter.org",
    license="BSD",
    platforms="Linux, Mac OS X",
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=install_requires,
    entry_points={
        'jupyterhub.spawners': [
            'docker = dockerspawner:DockerSpawner',
            'docker-system-user = dockerspawner:SystemUserSpawner',
            'docker-swarm = dockerspawner:SwarmSpawner',
        ],
    },
    python_requires=">=3.8",
    cmdclass={
        'bdist_egg': bdist_egg if 'bdist_egg' in sys.argv else bdist_egg_disabled,
    },
)


def main():
    setup(**setup_args)


if __name__ == '__main__':
    main()

"""Create a development and testing environment using a virtualenv."""

from __future__ import unicode_literals

import os
import subprocess


VENV_NAME = '.venv'
PYTHON = 'python3'

TESTS = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS = os.path.join(TESTS, 'requirements.pip')
WITH_VENV = os.path.join(TESTS, 'with_venv.sh')
VENV = os.path.abspath(os.path.join(TESTS, '..', VENV_NAME))


def call(*args):
    """Simple ``subprocess.call`` wrapper."""
    if subprocess.call(args):
        raise SystemExit('Error running {0}.'.format(args))


def pip_install(*args):
    """Install packages using pip inside the virtualenv."""
    call(PYTHON, '-m', 'venv', VENV_NAME)
    call(WITH_VENV, VENV_NAME, 'pip', 'install', *args)


if __name__ == '__main__':
    pip_install('-r', REQUIREMENTS)

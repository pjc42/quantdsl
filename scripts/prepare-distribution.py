#!/usr/bin/env python
import os
import subprocess
import sys

try:
    del os.environ['PYTHONPATH']
except KeyError:
    pass


def get_version():
    return [line.split('=')[1].strip().strip(",").strip("'") for line in open('../quantdsl/__init__.py').readlines() if '__version__' in line][0]


def build_and_test(cwd):
    # Declare temporary working directory variable.
    tmpcwd27 = os.path.join(cwd, 'tmpve2.7')
    tmpcwd34 = os.path.join(cwd, 'tmpve3.4')

    # Build and upload to Test PyPI.
    subprocess.check_call([sys.executable, 'setup.py', 'sdist', 'upload', '-r', 'pypitest'], cwd=cwd)

    for (tmpcwd, python_executable) in [(tmpcwd27, 'python2.7'), (tmpcwd34, 'python3.4')]:

        # Rebuild virtualenvs.
        rebuild_virtualenv(cwd, tmpcwd, python_executable)

        # Upgrade pip.
        subprocess.check_call(['bin/pip', 'install', '--upgrade', 'pip'], cwd=tmpcwd)

        # Install from dist folder.
        subprocess.check_call(['bin/pip', 'install', '..[test]'], cwd=tmpcwd)

        # Check installed tests all pass.
        test_installation(tmpcwd)

        # Rebuild virtualenvs.
        rebuild_virtualenv(cwd, tmpcwd, python_executable)

        # Install from Test PyPI.
        subprocess.check_call(['bin/pip', 'install', '--upgrade', 'pip'], cwd=tmpcwd)

        subprocess.check_call(['bin/pip', 'install', 'quantdsl[test]=='+get_version(),
                               '--index-url', 'https://testpypi.python.org/simple',
                               '--extra-index-url', 'https://pypi.python.org/simple'
                               ],
                               cwd=tmpcwd)

        # Check installed tests all pass.
        test_installation(tmpcwd)

        remove_virtualenv(cwd, tmpcwd)


def test_installation(tmpcwd):
    subprocess.check_call(['bin/python', '-m', 'dateutil.parser'], cwd=tmpcwd)
    subprocess.check_call(['bin/python', '-m' 'unittest', 'discover', 'quantdsl'], cwd=tmpcwd)


def rebuild_virtualenv(cwd, venv_path, python_executable):
    remove_virtualenv(cwd, venv_path)
    subprocess.check_call(['virtualenv', '-p', python_executable, venv_path], cwd=cwd)



def remove_virtualenv(cwd, venv_path):
    subprocess.check_call(['rm', '-rf', venv_path], cwd=cwd)


if __name__ == '__main__':
    cwd = os.path.join(os.environ['HOME'], 'PyCharmProjects', 'quantdsl')
    build_and_test(cwd)


#!/usr/bin/env python
import json
import locale
import os
import re
import subprocess
import sys


version_re = re.compile(r'\d+\.\d+(\.\d+)?')
exec_dir = os.path.dirname(sys.executable)


class EnvironmentException(Exception):
    pass


def detect_environment(dirname):
    """Determine the python dependencies in the environment.

    `pip freeze` will be used to introspect the environment.

    Returns a dictionary containing the package spec filename
    and contents if successful, or a dictionary containing 'error'
    on failure.
    """
    result = (output_file(dirname, 'environment.yml', 'conda') or
              output_file(dirname, 'requirements.txt', 'pip'))

    if result is None:
        if has_conda(os.environ):
            result = conda_env_export()
            result['conda'] = get_binary_version('conda')
        else:
            result = pip_freeze(dirname)
            result['pip'] = get_module_version('pip')

    if result is not None:
        result['python'] = get_python_version()
        result['locale'] = get_default_locale()

    return result


def get_python_version():
    v = sys.version_info
    return "%d.%d.%d" % (v[0], v[1], v[2])


def get_default_locale():
    return '.'.join(locale.getdefaultlocale())


def _parse_version_output(args, module):
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = proc.communicate()
        match = version_re.search(stdout or stderr)
        if match:
            return match.group()

        msg = "Failed to get version of '%s' from the output of: %s" % (module, ' '.join(args))
        raise EnvironmentException(msg)
    except Exception as exc:
        raise EnvironmentException("Error getting '%s' version: %s" % (module, str(exc)))


def get_module_version(module):
    args = [sys.executable, '-m', module, '--version']
    return _parse_version_output(args, module)


def get_binary_version(binary):
    args = [binary, '--version']
    return _parse_version_output(args, binary)


def output_file(dirname, filename, package_manager):
    """Read an existing package spec file.

    Returns a dictionary containing the filename and contents
    if successful, None if the file does not exist,
    or a dictionary containing 'error' on failure.
    """
    try:
        path = os.path.join(dirname, filename)
        if not os.path.exists(path):
            return None

        with open(path, 'r') as f:
            data = f.read()

        data = '\n'.join([line for line in data.split('\n')
                                if 'rsconnect' not in line])

        return {
            'filename': filename,
            'contents': data,
            'source': 'file',
            'package_manager': package_manager,
        }
    except Exception as exc:
        raise EnvironmentException('Error reading %s: %s' % (filename, str(exc)))


def pip_freeze(dirname):
    """Inspect the environment using `pip freeze`.

    Returns a dictionary containing the filename
    (always 'requirements.txt') and contents if successful,
    or a dictionary containing 'error' on failure.
    """
    try:
        proc = subprocess.Popen(
            [sys.executable, '-m', 'pip', 'freeze'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        pip_stdout, pip_stderr = proc.communicate()
        pip_status = proc.returncode
    except Exception as exc:
        raise EnvironmentException('Error during pip freeze: %s' % str(exc))

    if pip_status != 0:
        msg = pip_stderr or ('exited with code %d' % pip_status)
        raise EnvironmentException('Error during pip freeze: %s' % msg)

    pip_stdout = '\n'.join([line for line in pip_stdout.split('\n')
                            if 'rsconnect' not in line])

    return {
        'filename': 'requirements.txt',
        'contents': pip_stdout,
        'source': 'pip_freeze',
        'package_manager': 'pip',
    }


def has_conda(env):
    """Return true if there is current a conda environment active"""
    result = env.get('CONDA_PREFIX') or env.get('CONDA_DEFAULT_ENV')
    return result is not None


def conda_env_export():
    """Inspect the environment using `conda env export`.

    Returns a dictionary containing the filename
    (always 'environment.yml') and contents if successful,
    or raises an EnvironmentException on failure.
    """
    try:
        proc = subprocess.Popen(
            ['conda', 'env', 'export'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        stdout, stderr = proc.communicate()
        status = proc.returncode
    except Exception as exc:
        raise EnvironmentException('Error during conda env export: %s' % str(exc))

    if status != 0:
        msg = stderr or ('exited with code %d' % status)
        raise EnvironmentException('Error during conda env export: %s' % msg)

    return {
        'filename': 'environment.yml',
        'contents': stdout,
        'source': 'conda_env_export',
        'package_manager': 'conda',
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            raise EnvironmentException('Usage: %s DIRECTORY' % sys.argv[0])

        result = detect_environment(sys.argv[1])
    except EnvironmentException as exc:
        result = dict(error=str(exc))

    json.dump(result, sys.stdout, indent=4)

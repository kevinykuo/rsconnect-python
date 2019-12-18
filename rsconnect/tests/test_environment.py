import os
import re
import sys

from unittest import TestCase
from os.path import dirname, exists, join

from rsconnect.environment import detect_environment

version_re = re.compile(r'\d+\.\d+(\.\d+)?')

class TestEnvironment(TestCase):
    def get_dir(self, name):
        py_version = 'py%d' % sys.version_info[0]
        path = join(dirname(__file__), 'testdata', py_version, name)
        self.assertTrue(exists(path))
        return path

    def python_version(self):
    	return '.'.join(map(str, sys.version_info[:3]))

    def test_file(self):
        result = detect_environment(self.get_dir('pip1'), sys.executable)

        pip_version = result.pop('pip')
        self.assertTrue(version_re.match(pip_version))

        locale = result.pop('locale')
        self.assertIsInstance(locale, str)
        self.assertIn('.', locale)

        self.assertEqual(result, {
            'package_manager': 'pip',
            'source': 'file',
            'filename': 'requirements.txt',
            'contents': 'numpy\npandas\nmatplotlib\n',
            'python': self.python_version(),
        })

    def test_pip_freeze(self):
        result = detect_environment(self.get_dir('pip2'), sys.executable)
        contents = result.pop('contents')

        # these are the dependencies declared in our setup.py
        self.assertIn('six', contents)
        self.assertIn('Click', contents)

        pip_version = result.pop('pip')
        self.assertTrue(version_re.match(pip_version))

        locale = result.pop('locale')
        self.assertIsInstance(locale, str)
        self.assertIn('.', locale)

        self.assertEqual(result, {
            'package_manager': 'pip',
            'source': 'pip_freeze',
            'filename': 'requirements.txt',
            'python': self.python_version(),
        })

    def test_conda_env_export(self):
        os.environ['PATH'] = '/opt/anaconda/condabin' + os.pathsep + os.environ['PATH']
        result = detect_environment(self.get_dir('pip2'), '/opt/anaconda/envs/testenv/bin/python')
        contents = result.pop('contents')

        # these are the dependencies declared in our setup.py
        self.assertIn('six', contents)
        self.assertIn('Click', contents)

        conda_version = result.pop('conda')
        self.assertTrue(version_re.match(conda_version))

        locale = result.pop('locale')
        self.assertIsInstance(locale, str)
        self.assertIn('.', locale)

        # check python version. Note conda installed python might have different patch version.
        python_version = result.pop('python')
        self.assertEqual(python_version[:3], self.python_version()[:3])

        self.assertEqual(result, {
            'package_manager': 'conda',
            'source': 'conda_env_export',
            'filename': 'environment.yml',
        })

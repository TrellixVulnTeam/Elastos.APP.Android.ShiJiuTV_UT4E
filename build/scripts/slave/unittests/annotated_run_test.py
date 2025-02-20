#!/usr/bin/env python

# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tests that the tools/build annotated_run wrapper actually runs."""

import collections
import json
import logging
import os
import subprocess
import sys
import tempfile
import unittest

import test_env  # pylint: disable=W0403,W0611

import mock
from common import env
from slave import annotated_run
from slave import logdog_bootstrap
from slave import robust_tempdir
from slave import update_scripts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


MockOptions = collections.namedtuple('MockOptions',
    ('dry_run',))


class AnnotatedRunTest(unittest.TestCase):
  def test_example(self):
    build_properties = {
      'recipe': 'annotated_run_test',
      'true_prop': True,
      'num_prop': 123,
      'string_prop': '321',
      'dict_prop': {'foo': 'bar'},
    }

    script_path = os.path.join(BASE_DIR, 'annotated_run.py')
    exit_code = subprocess.call([
        'python', script_path,
        '--build-properties=%s' % json.dumps(build_properties)])
    self.assertEqual(exit_code, 0)

  @mock.patch('slave.update_scripts._run_command')
  @mock.patch('slave.annotated_run._run_command')
  @mock.patch('slave.annotated_run.main')
  @mock.patch('sys.platform', return_value='win')
  @mock.patch('tempfile.mkstemp', side_effect=Exception('failure'))
  def test_update_scripts_must_run(self, _tempfile_mkstemp, _sys_platform,
                                   main, annotated_run_command,
                                   update_scripts_run_command):
    update_scripts._run_command.return_value = (0, "")
    annotated_run._run_command.return_value = (0, "")
    annotated_run.main.side_effect = Exception('Test error!')
    annotated_run.shell_main(['annotated_run.py', 'foo'])

    gclient_path = os.path.join(env.Build, os.pardir, 'depot_tools',
                                'gclient.bat')
    annotated_run_command.assert_has_calls([
        mock.call([sys.executable, 'annotated_run.py', 'foo']),
        ])
    update_scripts_run_command.assert_has_calls([
        mock.call([gclient_path, 'sync', '--force', '--verbose', '--jobs=2',
                   '--break_repo_locks'],
                  cwd=env.Build),
        ])
    main.assert_not_called()


class AnnotatedRunExecTest(unittest.TestCase):
  def setUp(self):
    logging.basicConfig(level=logging.ERROR+1)

    self.maxDiff = None
    self._patchers = []
    map(self._patch, (
        mock.patch('slave.annotated_run._run_command'),
        mock.patch('slave.annotated_run._build_dir'),
        mock.patch('slave.annotated_run._builder_dir'),
        mock.patch('os.path.exists'),
        ))

    # Mock build and builder directories.
    annotated_run._build_dir.return_value = '/home/user/builder/build'
    annotated_run._builder_dir.return_value = '/home/user/builder'

    self.rt = robust_tempdir.RobustTempdir(prefix='annotated_run_test')
    self.basedir = self.rt.tempdir()
    self.tdir = self.rt.tempdir()
    self.opts = MockOptions(
        dry_run=False)
    self.properties = {
      'recipe': 'example/recipe',
      'mastername': 'master.random',
      'buildername': 'builder',
    }
    self.rpy_path = os.path.join(env.Build, 'scripts', 'slave', 'recipes.py')
    self.recipe_args = [
        sys.executable, '-u', self.rpy_path, '--verbose', 'run',
        '--workdir=/home/user/builder/build',
        '--properties-file=%s' % (self._tp('recipe_properties.json'),),
        'example/recipe']

    # Use public recipes.py path.
    os.path.exists.return_value = False

  def tearDown(self):
    self.rt.close()
    for p in reversed(self._patchers):
      p.stop()

  def _bp(self, *p):
    return os.path.join(*((self.basedir,) + p))

  def _tp(self, *p):
    return os.path.join(*((self.tdir,) + p))

  def _patch(self, patcher):
    self._patchers.append(patcher)
    patcher.start()
    return patcher

  def _assertRecipeProperties(self, value):
    # Double-translate "value", since JSON converts strings to unicode.
    value = json.loads(json.dumps(value))
    with open(self._tp('recipe_properties.json')) as fd:
      self.assertEqual(json.load(fd), value)

  def test_exec_successful(self):
    annotated_run._run_command.return_value = (0, '')

    rv = annotated_run._exec_recipe(self.rt, self.opts, self.basedir, self.tdir,
                                    self.properties)
    self.assertEqual(rv, 0)
    self._assertRecipeProperties(self.properties)

    annotated_run._run_command.assert_called_once_with(self.recipe_args,
                                                       dry_run=False)

  @mock.patch('slave.logdog_bootstrap.bootstrap')
  @mock.patch('slave.logdog_bootstrap.BootstrapState.get_result')
  def test_exec_with_logdog_bootstrap(self, bs_result, bootstrap):
    bootstrap.return_value = logdog_bootstrap.BootstrapState(
        ['logdog_bootstrap'] + self.recipe_args, '/path/to/result.json')
    bootstrap.return_value.get_result.return_value = 13
    annotated_run._run_command.return_value = (13, '')

    rv = annotated_run._exec_recipe(self.rt, self.opts, self.basedir, self.tdir,
                                    self.properties)

    self.assertEqual(rv, 13)
    annotated_run._run_command.assert_called_once_with(
        ['logdog_bootstrap'] + self.recipe_args, dry_run=False)
    self._assertRecipeProperties(self.properties)

  @mock.patch('slave.logdog_bootstrap.bootstrap',
              side_effect=Exception('Unhandled situation.'))
  def test_runs_directly_if_bootstrap_fails(self, bootstrap):
    annotated_run._run_command.return_value = (123, '')

    rv = annotated_run._exec_recipe(self.rt, self.opts, self.basedir, self.tdir,
                                    self.properties)
    self.assertEqual(rv, 123)

    bootstrap.assert_called_once()
    annotated_run._run_command.assert_called_once_with(self.recipe_args,
                                                       dry_run=False)

  @mock.patch('slave.logdog_bootstrap.bootstrap')
  @mock.patch('slave.logdog_bootstrap.BootstrapState.get_result')
  def test_runs_directly_if_logdog_error(self, bs_result, bootstrap):
    bootstrap.return_value = logdog_bootstrap.BootstrapState(
        ['logdog_bootstrap'] + self.recipe_args, '/path/to/result.json')
    bs_result.side_effect = logdog_bootstrap.BootstrapError()

    # Return a different error code depending on whether we're bootstrapping so
    # we can assert that specifically the non-bootstrapped error code is the one
    # that is returned.
    def get_error_code(args, **_kw):
      if len(args) > 0 and args[0] == 'logdog_bootstrap':
        return (1, '')
      return (2, '')
    annotated_run._run_command.side_effect = get_error_code

    rv = annotated_run._exec_recipe(self.rt, self.opts, self.basedir, self.tdir,
                                    self.properties)
    self.assertEqual(rv, 2)

    bootstrap.assert_called_once()
    bs_result.assert_called_once()
    annotated_run._run_command.assert_has_calls([
        mock.call(['logdog_bootstrap'] + self.recipe_args, dry_run=False),
        mock.call(self.recipe_args, dry_run=False),
    ])


if __name__ == '__main__':
  unittest.main()

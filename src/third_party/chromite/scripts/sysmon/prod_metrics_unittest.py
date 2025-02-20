# -*- coding: utf-8 -*-
# Copyright 2016 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unit tests for summarize_build_stats."""

from __future__ import absolute_import
from __future__ import print_function

import doctest
import mock

from chromite.lib import cros_test_lib
from chromite.scripts.sysmon import prod_metrics

# pylint: disable=protected-access


def load_tests(loader, standard_tests, pattern):
  del loader, pattern
  standard_tests.addTests(doctest.DocTestSuite(prod_metrics))
  return standard_tests


class TestModuleFunctions(cros_test_lib.TestCase):
  """Tests for prod_metrics module functions."""

  def test__get_hostname(self):
    self.assertEqual(prod_metrics._get_hostname(
        {'hostname': 'foo.example.com'}), 'foo')

  def test__get_hostname_of_hostname(self):
    self.assertEqual(prod_metrics._get_hostname({'hostname': 'foo'}), 'foo')

  def test__get_data_center(self):
    self.assertEqual(prod_metrics._get_data_center(
        {'hostname': 'foo.mtv.example.com'}), 'mtv')

  def test__get_data_center_of_hostname(self):
    with self.assertRaises(ValueError):
      prod_metrics._get_data_center({'hostname': 'foo'})


class TestProdHostReporter(cros_test_lib.TestCase):
  """Tests for ProdHostReporter."""

  def test_call(self):
    """Test ProdHostReporter reporting correctly."""
    servers = [
        prod_metrics.Server(hostname='sharanohiar',
                            data_center='mtv',
                            status='primary',
                            roles='shard',
                            created='2016-01-01 00:00:00',
                            modified='2016-01-02 00:00:00',
                            note=''),
    ]
    source = mock.NonCallableMock(['get_servers'])
    source.get_servers.side_effect = lambda: iter(servers)
    sink1 = mock.NonCallableMock(['write_servers'])
    sink2 = mock.NonCallableMock(['write_servers'])

    reporter = prod_metrics._ProdHostReporter(source, [sink1, sink2])
    reporter()

    sink1.write_servers.assert_called_once_with(servers)
    sink2.write_servers.assert_called_once_with(servers)


class TestAtestSource(cros_test_lib.TestCase):
  """Tests for AtestSource."""

  def test_query_atest_for_servers(self):
    """Test _QueryAtestForServer()."""
    source = prod_metrics._AtestSource('atest')
    with mock.patch('subprocess.check_output') as check_output:
      check_output.return_value = 'dummy atest output'
      source._query_atest_for_servers()
      check_output.assert_called_once_with(
          ['atest', 'server', 'list', '--json'])

  def test_get_servers(self):
    """Test get_servers()."""
    source = prod_metrics._AtestSource(atest_program='atest')
    with mock.patch.object(source, '_query_atest_for_servers') as query:
      query.return_value = (
          '[{"status": "primary", "roles": ["shard"],'
          ' "date_modified": "2016-12-13 20:41:54",'
          ' "hostname": "chromeos-server71.cbf.corp.google.com",'
          ' "note": null,'' "date_created": "2016-12-13 20:41:54"}]')
      got = list(source.get_servers())
    self.assertEqual(got,
                     [prod_metrics.Server(
                         hostname='chromeos-server71',
                         data_center='cbf',
                         status='primary',
                         roles=('shard',),
                         created='2016-12-13 20:41:54',
                         modified='2016-12-13 20:41:54',
                         note=None)])


class TestTsMonSink(cros_test_lib.TestCase):
  """Tests for TsMonSink."""

  def setUp(self):
    patcher = mock.patch('infra_libs.ts_mon.common.interface.state.store',
                         autospec=True)
    self.store = patcher.start()
    self.addCleanup(patcher.stop)

  def test_write_servers(self):
    """Test write_servers()."""
    servers = [
        prod_metrics.Server(
            hostname='harvestasha-xp',
            data_center='mtv',
            status='primary',
            roles=('scheduler', 'host_scheduler', 'suite_scheduler', 'afe'),
            created='2014-12-11 22:48:43',
            modified='2014-12-11 22:48:43',
            note=''),
        prod_metrics.Server(
            hostname='harvestasha-vista',
            data_center='mtv',
            status='primary',
            roles=('devserver',),
            created='2015-01-05 13:32:49',
            modified='2015-01-05 13:32:49',
            note=''),
    ]
    sink = prod_metrics._TsMonSink('prod_hosts/')
    sink.write_servers(servers)

    setter = self.store.set
    calls = [
        mock.call('prod_hosts/presence', ('mtv', 'harvestasha-xp'), None,
                  True, enforce_ge=mock.ANY),
        mock.call('prod_hosts/roles', ('mtv', 'harvestasha-xp'), None,
                  'afe,host_scheduler,scheduler,suite_scheduler',
                  enforce_ge=mock.ANY),
        mock.call('prod_hosts/presence', ('mtv', 'harvestasha-vista'), None,
                  True, enforce_ge=mock.ANY),
        mock.call('prod_hosts/roles', ('mtv', 'harvestasha-vista'), None,
                  'devserver', enforce_ge=mock.ANY),
    ]
    setter.assert_has_calls(calls)
    self.assertEqual(len(setter.mock_calls), len(calls))

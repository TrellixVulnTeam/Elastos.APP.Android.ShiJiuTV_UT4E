#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unit tests for classes in gtest_command.py."""

import os
import tempfile
import unittest

import test_env  # pylint: disable=W0611

from common import chromium_utils
from common import find_depot_tools  # pylint: disable=W0611
from common import gtest_utils

from testing_support import auto_stub

FAILURES = ['NavigationControllerTest.Reload',
            'NavigationControllerTest/SpdyNetworkTransTest.Constructor/0',
            'BadTest.TimesOut',
            'MoreBadTest.TimesOutAndFails',
            'SomeOtherTest.SwitchTypes',
            'SomeOtherTest.FAILS_ThisTestTimesOut']

FAILS_FAILURES = ['SomeOtherTest.FAILS_Bar']
FLAKY_FAILURES = ['SomeOtherTest.FLAKY_Baz']

TIMEOUT_MESSAGE = 'Killed (timed out).'

RELOAD_ERRORS = (r'C:\b\slave\chrome-release-snappy\build\chrome\browser'
r'\navigation_controller_unittest.cc:381: Failure' + """
Value of: -1
Expected: contents->controller()->GetPendingEntryIndex()
Which is: 0

""")

SPDY_ERRORS = (r'C:\b\slave\chrome-release-snappy\build\chrome\browser'
r'\navigation_controller_unittest.cc:439: Failure' + """
Value of: -1
Expected: contents->controller()->GetPendingEntryIndex()
Which is: 0

""")

SWITCH_ERRORS = (r'C:\b\slave\chrome-release-snappy\build\chrome\browser'
r'\navigation_controller_unittest.cc:615: Failure' + """
Value of: -1
Expected: contents->controller()->GetPendingEntryIndex()
Which is: 0

""" + r'C:\b\slave\chrome-release-snappy\build\chrome\browser'
r'\navigation_controller_unittest.cc:617: Failure' + """
Value of: contents->controller()->GetPendingEntry()
  Actual: true
Expected: false

""")

TIMEOUT_ERRORS = ('[61613:263:0531/042613:2887943745568888:ERROR:/b/slave'
'/chromium-rel-mac-builder/build/src/chrome/browser/extensions'
'/extension_error_reporter.cc(56)] Extension error: Could not load extension '
'from \'extensions/api_test/geolocation/no_permission\'. Manifest file is '
'missing or unreadable.')

MOREBAD_ERRORS = """
Value of: entry->page_type()
  Actual: 2
Expected: NavigationEntry::NORMAL_PAGE
"""

TEST_DATA = ("""
[==========] Running 7 tests from 3 test cases.
[----------] Global test environment set-up.
[----------] 1 test from HunspellTest
[ RUN      ] HunspellTest.All
[       OK ] HunspellTest.All (62 ms)
[----------] 1 test from HunspellTest (62 ms total)

[----------] 4 tests from NavigationControllerTest
[ RUN      ] NavigationControllerTest.Defaults
[       OK ] NavigationControllerTest.Defaults (48 ms)
[ RUN      ] NavigationControllerTest.Reload
%(reload_errors)s
[  FAILED  ] NavigationControllerTest.Reload (2 ms)
[ RUN      ] NavigationControllerTest.Reload_GeneratesNewPage
[       OK ] NavigationControllerTest.Reload_GeneratesNewPage (22 ms)
[ RUN      ] NavigationControllerTest/SpdyNetworkTransTest.Constructor/0
%(spdy_errors)s
[  FAILED  ] NavigationControllerTest/SpdyNetworkTransTest.Constructor/0 (2 ms)
[----------] 4 tests from NavigationControllerTest (74 ms total)

  YOU HAVE 2 FLAKY TESTS

[----------] 1 test from BadTest
[ RUN      ] BadTest.TimesOut
%(timeout_errors)s
""" % {'reload_errors': RELOAD_ERRORS,
       'spdy_errors': SPDY_ERRORS,
       'timeout_errors': TIMEOUT_ERRORS} +
'[0531/042642:ERROR:/b/slave/chromium-rel-mac-builder/build/src/chrome'
'/test/test_launcher/out_of_proc_test_runner.cc(79)] Test timeout (30000 ms) '
'exceeded for BadTest.TimesOut' + """
Handling SIGTERM.
Successfully wrote to shutdown pipe, resetting signal handler.
""" +
'[61613:19971:0531/042642:2887973024284693:INFO:/b/slave/chromium-rel-mac-'
'builder/build/src/chrome/browser/browser_main.cc(285)] Handling shutdown for '
'signal 15.' + """

[----------] 1 test from MoreBadTest
[ RUN      ] MoreBadTest.TimesOutAndFails
%(morebad_errors)s
""" % {'morebad_errors': MOREBAD_ERRORS} +
'[0531/042642:ERROR:/b/slave/chromium-rel-mac-builder/build/src/chrome/test'
'/test_launcher/out_of_proc_test_runner.cc(79)] Test timeout (30000 ms) '
'exceeded for MoreBadTest.TimesOutAndFails' + """
Handling SIGTERM.
Successfully wrote to shutdown pipe, resetting signal handler.
[  FAILED  ] MoreBadTest.TimesOutAndFails (31000 ms)

[----------] 5 tests from SomeOtherTest
[ RUN      ] SomeOtherTest.SwitchTypes
%(switch_errors)s
[  FAILED  ] SomeOtherTest.SwitchTypes (40 ms)
[ RUN      ] SomeOtherTest.Foo
[       OK ] SomeOtherTest.Foo (20 ms)
[ RUN      ] SomeOtherTest.FAILS_Bar
Some error message for a failing test.
[  FAILED  ] SomeOtherTest.FAILS_Bar (40 ms)
[ RUN      ] SomeOtherTest.FAILS_ThisTestTimesOut
""" %  {'switch_errors' : SWITCH_ERRORS} +
'[0521/041343:ERROR:test_launcher.cc(384)] Test timeout (5000 ms) '
'exceeded for SomeOtherTest.FAILS_ThisTestTimesOut' + """
[ RUN      ] SomeOtherTest.FLAKY_Baz
Some error message for a flaky test.
[  FAILED  ] SomeOtherTest.FLAKY_Baz (40 ms)
[----------] 2 tests from SomeOtherTest (60 ms total)

[----------] Global test environment tear-down
[==========] 8 tests from 3 test cases ran. (3750 ms total)
[  PASSED  ] 4 tests.
[  FAILED  ] 4 tests, listed below:
[  FAILED  ] NavigationControllerTest.Reload
[  FAILED  ] NavigationControllerTest/SpdyNetworkTransTest.Constructor/0
[  FAILED  ] SomeOtherTest.SwitchTypes
[  FAILED  ] SomeOtherTest.FAILS_ThisTestTimesOut

 1 FAILED TEST
  YOU HAVE 10 DISABLED TESTS

  YOU HAVE 2 FLAKY TESTS

program finished with exit code 1
""")

TEST_DATA_CRASH = """
[==========] Running 7 tests from 3 test cases.
[----------] Global test environment set-up.
[----------] 1 test from HunspellTest
[ RUN      ] HunspellTest.Crashes
Oops, this test crashed!
"""

TEST_DATA_MIXED_STDOUT = """
[==========] Running 3 tests from 3 test cases.
[----------] Global test environment set-up.

[----------] 1 tests from WebSocketHandshakeHandlerSpdy3Test
[ RUN      ] WebSocketHandshakeHandlerSpdy3Test.RequestResponse
[       OK ] WebSocketHandshakeHandlerSpdy3Test.RequestResponse (1 ms)
[----------] 1 tests from WebSocketHandshakeHandlerSpdy3Test (1 ms total)

[----------] 1 test from URLRequestTestFTP
[ RUN      ] URLRequestTestFTP.UnsafePort
FTP server started on port 32841...
sending server_data: {"host": "127.0.0.1", "port": 32841} (36 bytes)
starting FTP server[       OK ] URLRequestTestFTP.UnsafePort (300 ms)
[----------] 1 test from URLRequestTestFTP (300 ms total)

[ RUN      ] TestFix.TestCase
[1:2/3:WARNING:extension_apitest.cc(169)] Workaround for 177163,
prematurely stopping test
[       OK ] X (1000ms total)

[----------] 1 test from Crash
[ RUN      ] Crash.Test
Oops, this test crashed!
"""

VALGRIND_HASH = 'B254345E4D3B6A00'

VALGRIND_REPORT = """Leak_DefinitelyLost
1 (1 direct, 0 indirect) bytes in 1 blocks are lost in loss record 1 of 1
  operator new(unsigned long) (m_replacemalloc/vg_replace_malloc.c:1140)
  content::NavigationControllerTest_Reload::TestBody() (a/b/c/d.cc:1150)
Suppression (error hash=#%(hash)s#):
{
   <insert_a_suppression_name_here>
   Memcheck:Leak
   fun:_Znw*
   fun:_ZN31NavigationControllerTest_Reload8TestBodyEv
}""" % {'hash' : VALGRIND_HASH}

TEST_DATA_VALGRIND = """
[==========] Running 5 tests from 2 test cases.
[----------] Global test environment set-up.
[----------] 1 test from HunspellTest
[ RUN      ] HunspellTest.All
[       OK ] HunspellTest.All (62 ms)
[----------] 1 test from HunspellTest (62 ms total)

[----------] 4 tests from NavigationControllerTest
[ RUN      ] NavigationControllerTest.Defaults
[       OK ] NavigationControllerTest.Defaults (48 ms)
[ RUN      ] NavigationControllerTest.Reload
[       OK ] NavigationControllerTest.Reload (2 ms)
[ RUN      ] NavigationControllerTest.Reload_GeneratesNewPage
[       OK ] NavigationControllerTest.Reload_GeneratesNewPage (22 ms)
[ RUN      ] NavigationControllerTest/SpdyNetworkTransTest.Constructor/0
[       OK ] NavigationControllerTest/SpdyNetworkTransTest.Constructor/0 (2 ms)
[----------] 4 tests from NavigationControllerTest (74 ms total)

[----------] Global test environment tear-down
[==========] 5 tests from 1 test cases ran. (136 ms total)
[  PASSED  ] 5 tests.

### BEGIN MEMORY TOOL REPORT (error hash=#%(hash)s#)
%(report)s
### END MEMORY TOOL REPORT (error hash=#%(hash)s#)
program finished with exit code 255

""" % {'report': VALGRIND_REPORT, 'hash': VALGRIND_HASH}


FAILING_TESTS_OUTPUT = """
Failing tests:
ChromeRenderViewTest.FAILS_AllowDOMStorage
PrerenderBrowserTest.PrerenderHTML5VideoJs
"""

FAILING_TESTS_EXPECTED = ['ChromeRenderViewTest.FAILS_AllowDOMStorage',
                          'PrerenderBrowserTest.PrerenderHTML5VideoJs']


TEST_DATA_SHARD_0 = ("""Note: This is test shard 1 of 30.
[==========] Running 6 tests from 3 test cases.
[----------] Global test environment set-up.
[----------] 1 test from HunspellTest
[ RUN      ] HunspellTest.All
[       OK ] HunspellTest.All (62 ms)
[----------] 1 test from HunspellTest (62 ms total)

[----------] 1 test from BadTest
[ RUN      ] BadTest.TimesOut
%(timeout_errors)s
""" % {'timeout_errors': TIMEOUT_ERRORS} +
'[0531/042642:ERROR:/b/slave/chromium-rel-mac-builder/build/src/chrome/test'
'/test_launcher/out_of_proc_test_runner.cc(79)] Test timeout (30000 ms) '
'exceeded for BadTest.TimesOut' + """
Handling SIGTERM.
Successfully wrote to shutdown pipe, resetting signal handler.
""" +
'[61613:19971:0531/042642:2887973024284693:INFO:/b/slave/chromium-rel-mac-'
'builder/build/src/chrome/browser/browser_main.cc(285)] Handling shutdown for '
'signal 15.' + """

[----------] 4 tests from SomeOtherTest
[ RUN      ] SomeOtherTest.SwitchTypes
%(switch_errors)s
[  FAILED  ] SomeOtherTest.SwitchTypes (40 ms)
[ RUN      ] SomeOtherTest.Foo
[       OK ] SomeOtherTest.Foo (20 ms)
[ RUN      ] SomeOtherTest.FAILS_Bar
Some error message for a failing test.
[  FAILED  ] SomeOtherTest.FAILS_Bar (40 ms)
[ RUN      ] SomeOtherTest.FAILS_ThisTestTimesOut
"""  % {'switch_errors' : SWITCH_ERRORS} +
'[0521/041343:ERROR:test_launcher.cc(384)] Test timeout (5000 ms) exceeded '
'for SomeOtherTest.FAILS_ThisTestTimesOut' + """
[ RUN      ] SomeOtherTest.FLAKY_Baz
Some error message for a flaky test.
[  FAILED  ] SomeOtherTest.FLAKY_Baz (40 ms)
[----------] 2 tests from SomeOtherTest (60 ms total)

[----------] Global test environment tear-down
[==========] 7 tests from 3 test cases ran. (3750 ms total)
[  PASSED  ] 5 tests.
[  FAILED  ] 2 test, listed below:
[  FAILED  ] SomeOtherTest.SwitchTypes
[  FAILED  ] SomeOtherTest.FAILS_ThisTestTimesOut

 1 FAILED TEST
  YOU HAVE 10 DISABLED TESTS

  YOU HAVE 2 FLAKY TESTS
""")

TEST_DATA_SHARD_1 = ("""Note: This is test shard 13 of 30.
[==========] Running 5 tests from 2 test cases.
[----------] Global test environment set-up.
[----------] 4 tests from NavigationControllerTest
[ RUN      ] NavigationControllerTest.Defaults
[       OK ] NavigationControllerTest.Defaults (48 ms)
[ RUN      ] NavigationControllerTest.Reload
%(reload_errors)s
[  FAILED  ] NavigationControllerTest.Reload (2 ms)
[ RUN      ] NavigationControllerTest.Reload_GeneratesNewPage
[       OK ] NavigationControllerTest.Reload_GeneratesNewPage (22 ms)
[ RUN      ] NavigationControllerTest/SpdyNetworkTransTest.Constructor/0
%(spdy_errors)s
""" % {'reload_errors' : RELOAD_ERRORS,
       'spdy_errors'   : SPDY_ERRORS} +
'[  FAILED  ] NavigationControllerTest/SpdyNetworkTransTest.Constructor'
'/0 (2 ms)' + """
[----------] 4 tests from NavigationControllerTest (74 ms total)

  YOU HAVE 2 FLAKY TESTS

[----------] 1 test from MoreBadTest
[ RUN      ] MoreBadTest.TimesOutAndFails
%(morebad_errors)s
""" % {'morebad_errors': MOREBAD_ERRORS} +
'[0531/042642:ERROR:/b/slave/chromium-rel-mac-builder/build/src/chrome/test'
'/test_launcher/out_of_proc_test_runner.cc(79)] Test timeout (30000 ms) '
'exceeded for MoreBadTest.TimesOutAndFails' + """
Handling SIGTERM.
Successfully wrote to shutdown pipe, resetting signal handler.
[  FAILED  ] MoreBadTest.TimesOutAndFails (31000 ms)

[----------] Global test environment tear-down
[==========] 5 tests from 2 test cases ran. (3750 ms total)
[  PASSED  ] 3 tests.
[  FAILED  ] 2 tests, listed below:
[  FAILED  ] NavigationControllerTest.Reload
[  FAILED  ] NavigationControllerTest/SpdyNetworkTransTest.Constructor/0

 1 FAILED TEST
  YOU HAVE 10 DISABLED TESTS

  YOU HAVE 2 FLAKY TESTS
""")

TEST_DATA_SHARD_EXIT = 'program finished with exit code '

TEST_DATA_CRASH_SHARD = """Note: This is test shard 5 of 5.
[==========] Running 7 tests from 3 test cases.
[----------] Global test environment set-up.
[----------] 1 test from HunspellTest
[ RUN      ] HunspellTest.Crashes
Oops, this test crashed!"""

TEST_DATA_NESTED_RUNS = ("""
[ 1/3] 1.0s Foo.Bar (45.5s)
Note: Google Test filter = Foo.Bar
[==========] Running 1 test from 1 test case.
[----------] Global test environment set-up.
[----------] 1 test from Foo, where TypeParam =
[ RUN      ] Foo.Bar
""" +
'[0725/050653:ERROR:test_launcher.cc(380)] Test timeout (45000 ms) exceeded '
'for Foo.Bar' + """
Starting tests...
IMPORTANT DEBUGGING NOTE: each test is run inside its own process.
For debugging a test inside a debugger, use the
--gtest_filter=<your_test_name> flag along with either
--single_process (to run all tests in one launcher/browser process) or
--single-process (to do the above, and also run Chrome in single-
process mode).
1 test run
1 test failed (0 ignored)
Failing tests:
Foo.Bar
[ 2/2] 2.00s Foo.Pass (1.0s)""")


# Data generated with run_test_case.py
TEST_DATA_RUN_TEST_CASE_FAIL = """
[  6/422]   7.45s SUIDSandboxUITest.testSUIDSandboxEnabled (1.49s) - retry #2
[ RUN      ] SUIDSandboxUITest.testSUIDSandboxEnabled
[  FAILED  ] SUIDSandboxUITest.testSUIDSandboxEnabled (771 ms)
[  8/422]   7.76s PrintPreviewWebUITest.SourceIsPDFShowFitToPageOption (1.67s)
"""

TEST_DATA_RUN_TEST_CASE_TIMEOUT = """
[  6/422]   7.45s SUIDSandboxUITest.testSUIDSandboxEnabled (1.49s) - retry #2
[ RUN      ] SUIDSandboxUITest.testSUIDSandboxEnabled
(junk)
[  8/422]   7.76s PrintPreviewWebUITest.SourceIsPDFShowFitToPageOption (1.67s)
"""


# Data generated by swarming.py
TEST_DATA_SWARM_TEST_FAIL = """

================================================================
Begin output from shard index 0 (machine tag: swarm12.c, id: swarm12)
================================================================

[==========] Running 2 tests from linux_swarm_trigg-8-base_unittests test run.
Starting tests (using 2 parallel jobs)...
IMPORTANT DEBUGGING NOTE: batches of tests are run inside their
own process. For debugging a test inside a debugger, use the
--gtest_filter=<your_test_name> flag along with
--single-process-tests.
[1/1242] HistogramDeathTest.BadRangesTest (62 ms)
[2/1242] OutOfMemoryDeathTest.New (22 ms)
[1242/1242] ThreadIdNameManagerTest.ThreadNameInterning (0 ms)
Retrying 1 test (retry #1)
[ RUN      ] PickleTest.EncodeDecode
../../base/pickle_unittest.cc:69: Failure
Value of: false
  Actual: false
Expected: true
[  FAILED  ] PickleTest.EncodeDecode (0 ms)
[1243/1243] PickleTest.EncodeDecode (0 ms)
Retrying 1 test (retry #2)
[ RUN      ] PickleTest.EncodeDecode
../../base/pickle_unittest.cc:69: Failure
Value of: false
  Actual: false
Expected: true
[  FAILED  ] PickleTest.EncodeDecode (1 ms)
[1244/1244] PickleTest.EncodeDecode (1 ms)
Retrying 1 test (retry #3)
[ RUN      ] PickleTest.EncodeDecode
../../base/pickle_unittest.cc:69: Failure
Value of: false
  Actual: false
Expected: true
[  FAILED  ] PickleTest.EncodeDecode (0 ms)
[1245/1245] PickleTest.EncodeDecode (0 ms)
1245 tests run
1 test failed:
    PickleTest.EncodeDecode
Summary of all itest iterations:
1 test failed:
    PickleTest.EncodeDecode
End of the summary.
Tests took 31 seconds.


================================================================
End output from shard index 0 (machine tag: swarm12.c, id: swarm12). Return 1
================================================================

"""


class TestGTestLogParserTests(auto_stub.TestCase):

  def testGTestLogParserNoSharing(self):
    # Tests for log parsing without sharding.
    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA.splitlines():
      parser.ProcessLine(line)

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertFalse(parser.RunningTests())

    self.assertEqual(sorted(FAILURES), sorted(parser.FailedTests()))
    self.assertEqual(sorted(FAILURES + FAILS_FAILURES),
                     sorted(parser.FailedTests(include_fails=True)))
    self.assertEqual(sorted(FAILURES + FLAKY_FAILURES),
                     sorted(parser.FailedTests(include_flaky=True)))
    self.assertEqual(sorted(FAILURES + FAILS_FAILURES + FLAKY_FAILURES),
        sorted(parser.FailedTests(include_fails=True, include_flaky=True)))

    self.assertEqual(10, parser.DisabledTests())
    self.assertEqual(2, parser.FlakyTests())

    test_name = 'NavigationControllerTest.Reload'
    self.assertEqual('\n'.join(['%s: ' % test_name, RELOAD_ERRORS]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['FAILURE'], parser.TriesForTest(test_name))

    test_name = 'NavigationControllerTest/SpdyNetworkTransTest.Constructor/0'
    self.assertEqual('\n'.join(['%s: ' % test_name, SPDY_ERRORS]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['FAILURE'], parser.TriesForTest(test_name))

    test_name = 'SomeOtherTest.SwitchTypes'
    self.assertEqual('\n'.join(['%s: ' % test_name, SWITCH_ERRORS]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['FAILURE'], parser.TriesForTest(test_name))

    test_name = 'BadTest.TimesOut'
    self.assertEqual('\n'.join(['%s: ' % test_name,
                                TIMEOUT_ERRORS, TIMEOUT_MESSAGE]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['TIMEOUT'], parser.TriesForTest(test_name))

    test_name = 'MoreBadTest.TimesOutAndFails'
    self.assertEqual('\n'.join(['%s: ' % test_name,
                                MOREBAD_ERRORS, TIMEOUT_MESSAGE]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['TIMEOUT'], parser.TriesForTest(test_name))

    self.assertEqual(['SUCCESS'], parser.TriesForTest('SomeOtherTest.Foo'))

    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_CRASH.splitlines():
      parser.ProcessLine(line)

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertTrue(parser.RunningTests())
    self.assertEqual(['HunspellTest.Crashes'], parser.FailedTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(0, parser.FlakyTests())

    test_name = 'HunspellTest.Crashes'
    self.assertEqual('\n'.join(['%s: ' % test_name, 'Did not complete.']),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['UNKNOWN'], parser.TriesForTest(test_name))

  def testGTestLogParserSharing(self):
    # Same tests for log parsing with sharding_supervisor.
    parser = gtest_utils.GTestLogParser()
    test_data_shard = TEST_DATA_SHARD_0 + TEST_DATA_SHARD_1
    for line in test_data_shard.splitlines():
      parser.ProcessLine(line)
    parser.ProcessLine(TEST_DATA_SHARD_EXIT + '2')

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertFalse(parser.RunningTests())

    self.assertEqual(sorted(FAILURES), sorted(parser.FailedTests()))
    self.assertEqual(sorted(FAILURES + FAILS_FAILURES),
                     sorted(parser.FailedTests(include_fails=True)))
    self.assertEqual(sorted(FAILURES + FLAKY_FAILURES),
                     sorted(parser.FailedTests(include_flaky=True)))
    self.assertEqual(sorted(
        FAILURES + FAILS_FAILURES + FLAKY_FAILURES),
        sorted(parser.FailedTests(include_fails=True, include_flaky=True)))

    self.assertEqual(10, parser.DisabledTests())
    self.assertEqual(2, parser.FlakyTests())

    test_name = 'NavigationControllerTest.Reload'
    self.assertEqual('\n'.join(['%s: ' % test_name, RELOAD_ERRORS]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['FAILURE'], parser.TriesForTest(test_name))

    test_name = (
        'NavigationControllerTest/SpdyNetworkTransTest.Constructor/0')
    self.assertEqual('\n'.join(['%s: ' % test_name, SPDY_ERRORS]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['FAILURE'], parser.TriesForTest(test_name))

    test_name = 'SomeOtherTest.SwitchTypes'
    self.assertEqual('\n'.join(['%s: ' % test_name, SWITCH_ERRORS]),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['FAILURE'], parser.TriesForTest(test_name))

    test_name = 'BadTest.TimesOut'
    self.assertEqual(
        '\n'.join(['%s: ' % test_name,
        TIMEOUT_ERRORS, TIMEOUT_MESSAGE]),
        '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['TIMEOUT'], parser.TriesForTest(test_name))

    test_name = 'MoreBadTest.TimesOutAndFails'
    self.assertEqual(
        '\n'.join(['%s: ' % test_name,
        MOREBAD_ERRORS, TIMEOUT_MESSAGE]),
        '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['TIMEOUT'], parser.TriesForTest(test_name))

    self.assertEqual(['SUCCESS'], parser.TriesForTest('SomeOtherTest.Foo'))

    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_CRASH.splitlines():
      parser.ProcessLine(line)

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertTrue(parser.RunningTests())
    self.assertEqual(['HunspellTest.Crashes'], parser.FailedTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(0, parser.FlakyTests())

    test_name = 'HunspellTest.Crashes'
    self.assertEqual('\n'.join(['%s: ' % test_name, 'Did not complete.']),
                     '\n'.join(parser.FailureDescription(test_name)))
    self.assertEqual(['UNKNOWN'], parser.TriesForTest(test_name))

  def testGTestLogParserMixedStdout(self):
    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_MIXED_STDOUT.splitlines():
      parser.ProcessLine(line)

    self.assertEqual([], parser.ParsingErrors())
    self.assertEqual(['Crash.Test'], parser.RunningTests())
    self.assertEqual(['TestFix.TestCase', 'Crash.Test'], parser.FailedTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(0, parser.FlakyTests())
    self.assertEqual(['UNKNOWN'], parser.TriesForTest('Crash.Test'))
    self.assertEqual(['TIMEOUT'], parser.TriesForTest('TestFix.TestCase'))
    self.assertEqual(['SUCCESS'], parser.TriesForTest(
        'WebSocketHandshakeHandlerSpdy3Test.RequestResponse'))

  def testGTestLogParserValgrind(self):
    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_VALGRIND.splitlines():
      parser.ProcessLine(line)

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertFalse(parser.RunningTests())
    self.assertFalse(parser.FailedTests())
    self.assertEqual([VALGRIND_HASH], parser.MemoryToolReportHashes())
    self.assertEqual(VALGRIND_REPORT,
                     '\n'.join(parser.MemoryToolReport(VALGRIND_HASH)))
    self.assertEqual(['SUCCESS'], parser.TriesForTest('HunspellTest.All'))

    parser = gtest_utils.GTestLogParser()
    for line in FAILING_TESTS_OUTPUT.splitlines():
      parser.ProcessLine(line)
    self.assertEqual(FAILING_TESTS_EXPECTED,
                     parser.FailedTests(True, True))

  def testRunTestCaseFail(self):
    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_RUN_TEST_CASE_FAIL.splitlines():
      parser.ProcessLine(line)

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertEqual([], parser.RunningTests())
    self.assertEqual(
        ['SUIDSandboxUITest.testSUIDSandboxEnabled'], parser.FailedTests())
    self.assertEqual(
        ['SUIDSandboxUITest.testSUIDSandboxEnabled: '],
        parser.FailureDescription('SUIDSandboxUITest.testSUIDSandboxEnabled'))
    self.assertEqual(
        ['FAILURE'],
        parser.TriesForTest('SUIDSandboxUITest.testSUIDSandboxEnabled'))

  def testRunTestCaseTimeout(self):
    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_RUN_TEST_CASE_TIMEOUT.splitlines():
      parser.ProcessLine(line)

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertEqual([], parser.RunningTests())
    self.assertEqual(
        ['SUIDSandboxUITest.testSUIDSandboxEnabled'], parser.FailedTests())
    self.assertEqual(
        ['SUIDSandboxUITest.testSUIDSandboxEnabled: ', '(junk)'],
        parser.FailureDescription('SUIDSandboxUITest.testSUIDSandboxEnabled'))
    self.assertEqual(
        ['TIMEOUT'],
        parser.TriesForTest('SUIDSandboxUITest.testSUIDSandboxEnabled'))

  def testRunTestCaseParseSwarm(self):
    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_SWARM_TEST_FAIL.splitlines():
      parser.ProcessLine(line)

    self.assertEqual(0, len(parser.ParsingErrors()))
    self.assertEqual([], parser.RunningTests())
    self.assertEqual(
        ['PickleTest.EncodeDecode'], parser.FailedTests())
    self.assertEqual(
        [
          'PickleTest.EncodeDecode: ',
          '../../base/pickle_unittest.cc:69: Failure',
          'Value of: false',
          '  Actual: false',
          'Expected: true',
        ],
        parser.FailureDescription('PickleTest.EncodeDecode'))
    self.assertEqual(
        ['FAILURE'],
        parser.TriesForTest('PickleTest.EncodeDecode'))

  def testNestedGtests(self):
    parser = gtest_utils.GTestLogParser()
    for line in TEST_DATA_NESTED_RUNS.splitlines():
      parser.ProcessLine(line)
    self.assertEqual(['Foo.Bar'], parser.FailedTests(True, True))


class TestGTestJSONParserTests(auto_stub.TestCase):
  def testPassedTests(self):
    parser = gtest_utils.GTestJSONParser()
    parser.ProcessJSONData({
      'disabled_tests': [],
      'global_tags': [],
      'per_iteration_data': [
        {
          'Test.One': [{'status': 'SUCCESS', 'output_snippet': ''}],
          'Test.Two': [{'status': 'SUCCESS', 'output_snippet': ''}],
          'Test.Three': [{'status': 'SKIPPED', 'output_snippet': ''}],
        }
      ]
    })
    self.assertEqual(sorted(['Test.One', 'Test.Two', 'Test.Three']),
                     parser.PassedTests())
    self.assertEqual([], parser.FailedTests())
    self.assertEqual(0, parser.FlakyTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(['SUCCESS'], parser.TriesForTest('Test.One'))
    self.assertEqual(['SUCCESS'], parser.TriesForTest('Test.Two'))
    self.assertEqual(['SKIPPED'], parser.TriesForTest('Test.Three'))

  def testInvalidEscape(self):
    parser = gtest_utils.GTestJSONParser()
    parser.ProcessJSONData({
      'disabled_tests': [],
      'global_tags': [],
      'per_iteration_data': [
        {
          'Test.One': [{'status': 'SUCCESS', 'output_snippet': '\\x5'}],
          'Test.Two': [{'status': 'SUCCESS', 'output_snippet': ''}],
        }
      ]
    })
    self.assertEqual(['Test.One', 'Test.Two'], parser.PassedTests())
    self.assertEqual([], parser.FailedTests())
    self.assertEqual(0, parser.FlakyTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(['SUCCESS'], parser.TriesForTest('Test.One'))
    self.assertEqual(['SUCCESS'], parser.TriesForTest('Test.Two'))

  def testFailedTests(self):
    parser = gtest_utils.GTestJSONParser()
    parser.ProcessJSONData({
      'disabled_tests': [],
      'global_tags': [],
      'per_iteration_data': [
        {
          'Test.One': [{'status': 'FAILURE', 'output_snippet': ''}],
          'Test.Two': [{'status': 'FAILURE', 'output_snippet': ''}],
        }
      ]
    })

    self.assertEqual([], parser.PassedTests())
    self.assertEqual(['Test.One', 'Test.Two'], parser.FailedTests())
    self.assertEqual(0, parser.FlakyTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(['FAILURE'], parser.TriesForTest('Test.One'))
    self.assertEqual(['FAILURE'], parser.TriesForTest('Test.Two'))

  def testFlakyTests(self):
    parser = gtest_utils.GTestJSONParser()
    parser.ProcessJSONData({
      'disabled_tests': [],
      'global_tags': [],
      'per_iteration_data': [
        {
          'Test.One': [{'status': 'FAILURE', 'output_snippet': ''}],
          'Test.Two': [
            {'status': 'FAILURE', 'output_snippet': ''},
            {'status': 'SUCCESS', 'output_snippet': ''},
          ],
        }
      ]
    })

    self.assertEqual(['Test.Two'], parser.PassedTests())
    self.assertEqual(['Test.One'], parser.FailedTests())
    self.assertEqual(1, parser.FlakyTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(['FAILURE'], parser.TriesForTest('Test.One'))
    self.assertEqual(['FAILURE', 'SUCCESS'], parser.TriesForTest('Test.Two'))

  def testRetriedTests(self):
    parser = gtest_utils.GTestJSONParser()
    parser.ProcessJSONData({
      'disabled_tests': [],
      'global_tags': [],
      'per_iteration_data': [
        {
          'Test.One': [
            {'status': 'FAILURE', 'output_snippet': ''},
            {'status': 'FAILURE', 'output_snippet': ''},
          ],
          'Test.Two': [
            {'status': 'FAILURE', 'output_snippet': ''},
            {'status': 'FAILURE_ON_EXIT', 'output_snippet': ''},
            {'status': 'CRASH', 'output_snippet': ''},
            {'status': 'TIMEOUT', 'output_snippet': ''},
            {'status': 'SKIPPED', 'output_snippet': ''},
            {'status': 'SUCCESS', 'output_snippet': ''},
          ],
        }
      ]
    })
    expected_tries_test_two = [
      'FAILURE',
      'FAILURE_ON_EXIT',
      'CRASH',
      'TIMEOUT',
      'SKIPPED',
      'SUCCESS'
    ]

    self.assertEqual(['Test.Two'], parser.PassedTests())
    self.assertEqual(['Test.One'], parser.FailedTests())
    self.assertEqual(1, parser.FlakyTests())
    self.assertEqual(0, parser.DisabledTests())
    self.assertEqual(['FAILURE', 'FAILURE'], parser.TriesForTest('Test.One'))
    self.assertEqual(expected_tries_test_two, parser.TriesForTest('Test.Two'))

  def testDisabledTests(self):
    parser = gtest_utils.GTestJSONParser()
    parser.ProcessJSONData({
      'disabled_tests': ['Test.Two'],
      'global_tags': [],
      'per_iteration_data': [
        {
          'Test.One': [{'status': 'SUCCESS', 'output_snippet': ''}],
        }
      ]
    })

    self.assertEqual(['Test.One'], parser.PassedTests())
    self.assertEqual([], parser.FailedTests())
    self.assertEqual(0, parser.FlakyTests())
    self.assertEqual(1, parser.DisabledTests())
    self.assertEqual(['SUCCESS'], parser.TriesForTest('Test.One'))
    self.assertEqual(['UNKNOWN'], parser.TriesForTest('Test.Two'))

  def testIngoredFailedTests(self):
    TEST_IGNORED_FAILED_TESTS_SPEC = """
      # A comment.

      crbug.com/12345 [ OS_WIN  , OS_LINUX] Test.One
      crbug.com/12345 [OS_WIN CPU_64_BITS MODE_RELEASE] Test.Two/2
      crbug.com/12345 [,OS_MACOSX, OS_WIN CPU_64_BITS, ] Perf/Test.Three
      crbug.com/12345 [ invalid.platform.spec ] Test.Four
      crbug.com/12345 [ OS_WIN CPU_32_BITS MODE_RELEASE ] Test.Five
      invalid line
    """

    _, spec_filename = tempfile.mkstemp()
    spec_fd = open(spec_filename, 'w')
    spec_fd.write(TEST_IGNORED_FAILED_TESTS_SPEC)
    spec_fd.close()

    self.mock(chromium_utils, 'FindUpward', lambda *_: spec_filename)
    parser = gtest_utils.GTestJSONParser()

    try:
      parser.ProcessJSONData({
        'disabled_tests': ['Test.Six'],
        'per_iteration_data': [
          {
            'Test.One': [{'status': 'FAILURE', 'output_snippet': ''}],
            'Test.Two/2': [{'status': 'FAILURE', 'output_snippet': ''}],
            'Perf/Test.Three': [{'status': 'FAILURE', 'output_snippet': ''}],
            'Test.Four': [{'status': 'FAILURE', 'output_snippet': ''}],
            'Test.Five': [{'status': 'FAILURE', 'output_snippet': ''}],
          }
        ],
        'global_tags': ['OS_WIN', 'CPU_64_BITS', 'MODE_RELEASE', 'OTHER_FLAG']
      }, '/fake/path/to/build')
    finally:
      os.remove(spec_filename)

    self.assertEqual(['Test.Five', 'Test.Four'], parser.FailedTests())
    self.assertEqual(['Perf/Test.Three', 'Test.One', 'Test.Two/2'],
                     parser.IgnoredFailedTests())
    self.assertEqual(['FAILURE'], parser.TriesForTest('Test.One'))
    self.assertEqual(['FAILURE'], parser.TriesForTest('Test.Two/2'))
    self.assertEqual(['FAILURE'], parser.TriesForTest('Perf/Test.Three'))
    self.assertEqual(['FAILURE'], parser.TriesForTest('Test.Four'))
    self.assertEqual(['FAILURE'], parser.TriesForTest('Test.Five'))

  # pylint: disable=R0201
  def testDoesNotThrowExceptionOnMissingIgnoredFailedTestsFile(self):
    parser = gtest_utils.GTestJSONParser()
    parser.ProcessJSONData({
      'disabled_tests': [],
      'global_tags': [],
      'per_iteration_data': []},
      tempfile.gettempdir())

  def testCompressList(self):
    CompressList = gtest_utils.CompressList
    self.assertEqual(['foo'], CompressList([1, 2, 3, 4], 0, 'foo'))
    self.assertEqual(['foo', 4], CompressList([1, 2, 3, 4], 1, 'foo'))
    self.assertEqual([1, 'foo', 4], CompressList([1, 2, 3, 4], 2, 'foo'))
    self.assertEqual([1, 'foo', 3, 4], CompressList([1, 2, 3, 4], 3, 'foo'))
    self.assertEqual([1, 2, 3, 4], CompressList([1, 2, 3, 4], 4, 'foo'))
    self.assertEqual([1, 2, 3, 4], CompressList([1, 2, 3, 4], 5, 'foo'))
    self.assertEqual([1, 2, 3, 4], CompressList([1, 2, 3, 4], 6, 'foo'))


if __name__ == '__main__':
  unittest.main()

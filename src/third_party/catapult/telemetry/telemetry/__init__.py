# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A library for cross-platform browser tests."""
import os
import sys
import glob

try:
  # This enables much better stack upon native code crashes.
  import faulthandler
  faulthandler.enable()
except ImportError:
  pass

# Ensure Python >= 2.7.
if sys.version_info < (2, 7):
  print >> sys.stderr, 'Need Python 2.7 or greater.'
  sys.exit(-1)


def _JoinPath(*path_parts):
  return os.path.abspath(os.path.join(*path_parts))


def _InsertPath(path):
  assert os.path.isdir(path), 'Not a valid path: %s' % path
  if path not in sys.path:
    # Some call sites that use Telemetry assume that sys.path[0] is the
    # directory containing the script, so we add these extra paths to right
    # after sys.path[0].
    sys.path.insert(1, path)


def _AddDirToPythonPath(*path_parts):
  path = _JoinPath(*path_parts)
  _InsertPath(path)


# Matches only 0 or 1 glob results
def _AddOptionalSingleGlobToPythonPath(*match_path_parts):
  absolute_match_path = _JoinPath(*match_path_parts)
  paths = glob.glob(absolute_match_path)
  if len(paths) > 1:
    raise ImportError('More than one result was found for glob {}'
                      .format(absolute_match_path))
  for path in paths:
    _InsertPath(path)


# Add Catapult dependencies to our path.
# util depends on py_utils, so we can't use it to get the catapult dir.
_CATAPULT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..')
_AddDirToPythonPath(_CATAPULT_DIR, 'common', 'py_utils')
_AddDirToPythonPath(_CATAPULT_DIR, 'dependency_manager')
_AddDirToPythonPath(_CATAPULT_DIR, 'devil')
_AddDirToPythonPath(_CATAPULT_DIR, 'systrace')
_AddDirToPythonPath(_CATAPULT_DIR, 'tracing')
_AddDirToPythonPath(_CATAPULT_DIR, 'common', 'py_trace_event')
_AddDirToPythonPath(_CATAPULT_DIR, 'common', 'battor')
_AddDirToPythonPath(_CATAPULT_DIR, 'common', 'py_vulcanize')
_AddDirToPythonPath(_CATAPULT_DIR, 'tracing', 'tracing_build')

from telemetry.core import util
from telemetry.internal.util import global_hooks

# Add Catapult third party dependencies into our path.
_AddDirToPythonPath(util.GetCatapultThirdPartyDir(), 'typ')
# Required by websocket-client.
_AddDirToPythonPath(util.GetCatapultThirdPartyDir(), 'six')

# Add Telemetry third party dependencies into our path.
_TELEMETRY_3P = util.GetTelemetryThirdPartyDir()
_AddDirToPythonPath(util.GetTelemetryThirdPartyDir(), 'altgraph')
_AddDirToPythonPath(util.GetTelemetryThirdPartyDir(), 'mock')
_AddDirToPythonPath(util.GetTelemetryThirdPartyDir(), 'modulegraph')
_AddDirToPythonPath(util.GetTelemetryThirdPartyDir(), 'mox3')
_AddDirToPythonPath(util.GetTelemetryThirdPartyDir(), 'png')
_AddDirToPythonPath(util.GetTelemetryThirdPartyDir(), 'pyfakefs')
_AddDirToPythonPath(util.GetTelemetryThirdPartyDir(), 'websocket-client')
# Chromium's vpython environment already provides these modules as wheels.
if not os.getenv('VIRTUAL_ENV'):
  _AddOptionalSingleGlobToPythonPath(_TELEMETRY_3P, 'cv2', 'lib', 'cv2_*')
  _AddOptionalSingleGlobToPythonPath(_TELEMETRY_3P, 'numpy', 'lib', 'numpy_*')

# Install Telemtry global hooks.
global_hooks.InstallHooks()

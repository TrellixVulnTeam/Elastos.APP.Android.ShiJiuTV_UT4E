#!/usr/bin/env python
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""cipd.py bootstraps a CIPD client and installs named CIPD packages to a
directory.
"""

import argparse
import collections
import json
import logging
import os
import subprocess
import sys
import tempfile

# Install Infra build environment.
BUILD_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
                             os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BUILD_ROOT, 'scripts'))

import common.env
import slave.infra_platform

# Instance-wide logger.
LOGGER = logging.getLogger('cipd')

# Used to contain a CIPD package specification.
CipdPackage = collections.namedtuple('CipdPackage', ('name', 'version'))

# A CIPD binary description - relative path of the binary within the package.
CipdBinary = collections.namedtuple('CipdBinary', ('package', 'relpath'))


def bootstrap(path):
  bootstrap_path = os.path.join(common.env.Build, 'scripts', 'slave',
                                'recipe_modules', 'cipd', 'resources',
                                'bootstrap.py')

  plat, bits = slave.infra_platform.get()
  plat = '%s-%s' % (
      plat.replace('win', 'windows'),
      {
          32: '386',
          64: 'amd64',
      }[bits]
  )
  json_output = os.path.join(path, 'cipd_bootstrap.json')

  cmd = [
    sys.executable,
    bootstrap_path,
    '--platform', plat,
    '--dest-directory', path,
    '--json-output', json_output,
  ]
  LOGGER.debug('Installing CIPD client: %s', cmd)
  subprocess.check_call(cmd)

  with open(json_output, 'r') as fd:
    return json.load(fd)['executable']


def cipd_ensure(client, path, packages, service_account_json=None,
                json_output=None):
  manifest_path = os.path.join(path, 'cipd_manifest.txt')
  with open(manifest_path, 'w') as fd:
    fd.write('# This file is autogenerated by %s\n\n' % (
             os.path.abspath(__file__),))
    for pkg in packages:
      LOGGER.debug('Adding package [%s] version [%s] to manifest.',
                   pkg.name, pkg.version)
      fd.write('%s  %s\n' % (pkg.name, pkg.version))

  cmd = [
      client,
      'ensure',
      '-list', manifest_path,
      '-root', path,
  ]
  if service_account_json:
    cmd += ['-service-account-json', service_account_json]
  if json_output:
    cmd += ['-json-output', json_output]
  LOGGER.debug('Ensuring CIPD packages: %s', cmd)
  subprocess.check_call(cmd)


def parse_cipd_package(v):
  idx = v.index('@')
  if idx > 0:
    package, version = v[:idx], v[idx+1:]
    if package and version:
      return CipdPackage(package, version)
  raise argparse.ArgumentTypeError('Package must be expressed using the format '
                                   '"PACKAGE@VERSION".')


def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', '--verbose', action='count',
                      help='Increase logging. Can be specified multiple times.')
  parser.add_argument('-P', '--package', metavar='PACKAGE@VERSION',
                      action='append', default=[], required=True,
                      type=parse_cipd_package,
                      help='Add a <package:version> to the CIPD manifest.')
  parser.add_argument('-d', '--dest-directory', required=True,
                      help='The CIPD package destination directory.')
  parser.add_argument('-o', '--json-output',
                      help='Output package results to a JSON file.')
  parser.add_argument('--service-account-json',
                      help='If specified, use this service account JSON.')
  opts = parser.parse_args(argv[1:])

  # Verbosity.
  if opts.verbose == 0:
    level = logging.WARNING
  elif opts.verbose == 1:
    level = logging.INFO
  else:
    level = logging.DEBUG
  logging.getLogger().setLevel(level)

  if not os.path.isdir(opts.dest_directory):
    LOGGER.info('Creating destination directory: %s', opts.dest_directory)
    os.makedirs(opts.dest_directory)

  LOGGER.debug('Bootstrapping CIPD client...')
  client = bootstrap(opts.dest_directory)
  LOGGER.info('Using CIPD client at [%s].', client)

  LOGGER.info('CIPD ensuring %d package(s)...', len(opts.package))
  cipd_ensure(client, opts.dest_directory, opts.package,
              service_account_json=opts.service_account_json,
              json_output=opts.json_output)
  return 0


if __name__ == '__main__':
  logging.basicConfig(level=logging.WARNING)
  sys.exit(main(sys.argv))

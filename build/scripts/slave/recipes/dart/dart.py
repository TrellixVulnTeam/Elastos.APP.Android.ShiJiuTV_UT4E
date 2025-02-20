# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from recipe_engine.recipe_api import Property

DEPS = [
  'depot_tools/bot_update',
  'file',
  'depot_tools/gclient',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
  'recipe_engine/python',
  'recipe_engine/step',
  'test_utils',
]

def RunSteps(api):
  buildername = str(api.properties.get('buildername')) # Convert from unicode.

  api.gclient.set_config('dart')

  if 'vm-precomp-android' in buildername:
    api.gclient.apply_config('android')

  api.bot_update.ensure_checkout(force=True)
  api.gclient.runhooks()

  extra_build_args = api.properties.get('build_args', [])
  mode = api.properties.get('mode', 'release')
  target_arch = api.properties.get('target_arch', 'x64')
  build_targets = api.properties.get('build_targets', ['runtime', 'create_sdk'])
  build_args = ['-m%s' % mode, '--arch=%s' % target_arch]
  build_args.extend(extra_build_args)
  build_args.extend(build_targets)
  api.python('build dart',
             api.path['checkout'].join('tools', 'build.py'),
             args=build_args,
             cwd=api.path['checkout'])

  with api.step.defer_results():
    extra_test_args = api.properties.get('test_args', [])
    test_args = ['-m%s' % mode,
                 '--arch=%s' % target_arch,
                 '--progress=line',
                 '--report',
                 '--time',
                 '--failure-summary',
                 '--write-debug-log',
                 '--write-test-outcome-log',
                 '--copy-coredumps']
    test_args.extend(extra_test_args)
    api.python('test vm',
               api.path['checkout'].join('tools', 'test.py'),
               args=test_args,
               cwd=api.path['checkout'])

def GenTests(api):
   yield (
      api.test('linux64') + api.platform('linux', 64) +
      api.properties.generic(mastername='client.dart.FYI'))
   yield (
      api.test('test-coverage') + api.platform('linux', 64) +
      api.properties.generic(mastername='client.dart.FYI',
                             buildername='vm-precomp-android-release',
                             target_arch='arm',
                             build_args=['--os=android'],
                             build_targets=['runtime_precompiled'],
                             test_args=[
                                 '-cprecompiler',
                                 '-rdart_precompiled',
                                 '--exclude-suite=pkg',
                                 '--system=android']))

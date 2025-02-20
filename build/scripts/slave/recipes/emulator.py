# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from recipe_engine import recipe_api
from recipe_engine.recipe_api import Property
from recipe_engine.types import freeze

DEPS = [
  'depot_tools/bot_update',
  'chromium',
  'chromium_android',
  'emulator',
  'depot_tools/gclient',
  'recipe_engine/path',
  'recipe_engine/properties',
  'recipe_engine/step',
]

REPO_URL = 'https://chromium.googlesource.com/chromium/src.git'

UNITTESTS = freeze([
  'android_webview_unittests',
  'base_unittests',
  'cc_unittests',
  'components_unittests',
  'events_unittests',
  'gl_tests',
  'ipc_tests',
  'skia_unittests',
  'sql_unittests',
  'sync_unit_tests',
  'ui_android_unittests',
  'ui_touch_selection_unittests',
])

BUILDERS = freeze({
  'chromium.fyi':{
    'Android Tests (x86 emulator)': {
      'config': 'x86_builder_mb',
      'target': 'Debug',
      'abi': 'x86',
      'api_level': 23,
      'unittests': UNITTESTS,
      'sdcard_size': '500M',
      'storage_size': '1024M'
    }
  }
})


PROPERTIES = {
  'buildername': Property(),
  'mastername': Property(),
}

def RunSteps(api, mastername, buildername):
  builder = BUILDERS[mastername][buildername]
  api.chromium_android.configure_from_properties(
      builder['config'],
      REPO_NAME='src',
      REPO_URL=REPO_URL,
      INTERNAL=False,
      BUILD_CONFIG=builder['target'])

  api.gclient.set_config('chromium')
  api.gclient.apply_config('android')
  api.emulator.set_config('base_config')

  api.bot_update.ensure_checkout()
  api.chromium_android.clean_local_files()
  api.chromium.runhooks()

  if api.chromium.c.project_generator.tool == 'mb':
    api.chromium.run_mb(mastername, buildername, use_goma=True)

  targets = []
  for target in builder.get('unittests', []):
    # TODO(agrieve): Remove _apk suffix in favour of bin/run_${target} once GYP
    #     is gone. http://crbug.com/599919
    targets.append(target + '_apk')
  api.chromium.compile(targets=targets)

  api.emulator.install_emulator_deps(api_level=builder.get('api_level'))

  provision_settings = builder.get('provision_provision_settings', {})

  default_emulator_amount = 1
  with api.emulator.launch_emulator(
      abi=builder.get('abi'),
      api_level=builder.get('api_level'),
      amount=builder.get('amount', default_emulator_amount),
      partition_size=builder.get('partition_size'),
      sdcard_size=builder.get('sdcard_size')):
    api.emulator.wait_for_emulator(builder.get('amount',
                                               default_emulator_amount))
    api.chromium_android.spawn_logcat_monitor()
    api.chromium_android.provision_devices(emulators=True, **provision_settings)

    try:
      with api.step.defer_results():
        for suite in builder.get('unittests', []):
          api.chromium_android.run_test_suite(suite)
    finally:
      api.chromium_android.logcat_dump()
      api.chromium_android.stack_tool_steps()
      api.chromium_android.test_report()

def GenTests(api):
  sanitize = lambda s: ''.join(c if c.isalnum() else '_' for c in s)

  for mastername in BUILDERS:
    master = BUILDERS[mastername]
    for buildername in master:
      yield (
          api.test('%s_test_basic' % sanitize(buildername)) +
          api.properties.generic(
              buildername=buildername,
              mastername=mastername))

  yield (
      api.test('Android_Tests__x86_emulator__test_fail') +
      api.properties.generic(
        buildername='Android Tests (x86 emulator)',
        mastername='chromium.fyi') +
      api.step_data('android_webview_unittests', retcode=2)
  )

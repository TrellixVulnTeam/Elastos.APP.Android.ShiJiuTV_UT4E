# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DEPS = [
  'adb',
  'bisect_tester',
  'depot_tools/bot_update',
  'chromium',
  'chromium_android',
  'chromium_swarming',
  'chromium_tests',
  'commit_position',
  'file',
  'isolate',
  'gsutil',
  'recipe_engine/json',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
  'recipe_engine/python',
  'recipe_engine/raw_io',
  'recipe_engine/step',
  'recipe_engine/tempfile',
  'swarming',
  'test_results',
  'test_utils',
]

from recipe_engine import config_types

def ignore_undumpable(obj):  # pragma: no cover
  try:
    return config_types.json_fixup(obj)
  except TypeError:
    return None


def RunSteps(api):
  # build/tests/masters_recipes_tests.py needs to manipulate the BUILDERS
  # dict, so we provide an API to dump it here.
  if api.properties.get('dump_builders'):  # pragma: no cover
    api.file.write(
        'Dump BUILDERS dict', api.properties['dump_builders'],
        api.json.dumps(api.chromium_tests.builders, default=ignore_undumpable))
    return

  mastername = api.properties.get('mastername')
  buildername = api.properties.get('buildername')

  bot_config = api.chromium_tests.create_bot_config_object(
      mastername, buildername)
  api.chromium_tests.configure_build(bot_config)
  update_step, bot_db = api.chromium_tests.prepare_checkout(
      bot_config, force=True)
  tests, tests_including_triggered = api.chromium_tests.get_tests(
      bot_config, bot_db)
  compile_targets = api.chromium_tests.get_compile_targets(
      bot_config, bot_db, tests_including_triggered)
  api.chromium_tests.compile_specific_targets(
      bot_config, update_step, bot_db,
      compile_targets, tests_including_triggered)
  api.chromium_tests.archive_build(
      mastername, buildername, update_step, bot_db)
  api.chromium_tests.download_and_unzip_build(mastername, buildername,
                                              update_step, bot_db)

  if not tests:
    return

  api.chromium_swarming.configure_swarming(
      'chromium', precommit=False, mastername=mastername)
  test_runner = api.chromium_tests.create_test_runner(
      api, tests, serialize_tests=bot_config.get('serialize_tests'))
  with api.chromium_tests.wrap_chromium_tests(bot_config, tests):
    test_runner()


def _sanitize_nonalpha(text):
  return ''.join(c if c.isalnum() else '_' for c in text)


def GenTests(api):
  for mastername, master_config in api.chromium_tests.builders.iteritems():

    # parent builder name -> list of triggered builders.
    triggered_by_parent = {}
    for buildername, bot_config in master_config['builders'].iteritems():
      parent = bot_config.get('parent_buildername')
      if parent:
        triggered_by_parent.setdefault(parent, []).append(buildername)

    for buildername, bot_config in master_config['builders'].iteritems():
      bot_type = bot_config.get('bot_type', 'builder_tester')

      if bot_type in ['builder', 'builder_tester']:
        assert bot_config.get('parent_buildername') is None, (
            'Unexpected parent_buildername for builder %r on master %r.' %
                (buildername, mastername))

      properties = {
        'mastername': mastername,
        'buildername': buildername,
        'parent_buildername': bot_config.get('parent_buildername'),
        'build_data_dir': api.path['root'].join('build_data_dir'),
        'path_config': 'kitchen',
      }
      if mastername == 'chromium.webkit':
        properties['gs_acl'] = 'public-read'
      if buildername == 'Android Find Annotated Test':
        properties['current_time'] = '20160101T000000'
      test = (
        api.test('full_%s_%s' % (_sanitize_nonalpha(mastername),
                                 _sanitize_nonalpha(buildername))) +
        api.properties.generic(**properties) +
        api.platform(bot_config['testing']['platform'],
                     bot_config.get(
                         'chromium_config_kwargs', {}).get('TARGET_BITS', 64))
      )

      if bot_config.get('parent_buildername'):
        test += api.properties(parent_got_revision='1111111')
        test += api.properties(
            parent_build_archive_url='gs://test-domain/test-archive.zip')

      if mastername == 'client.v8.fyi':
        test += api.properties(revision='22135')

      if bot_config.get('enable_swarming'):
        if bot_type == 'tester':
          test += api.properties(swarm_hashes={
            'browser_tests': 'ffffffffffffffffffffffffffffffffffffffff',
          })

        builders_with_tests = []
        if bot_type == 'builder':
          builders_with_tests = triggered_by_parent.get(buildername, [])
        else:
          builders_with_tests = [buildername]

        test_spec_name = bot_config.get('testing', {}).get(
            'test_spec_file', mastername + '.json')
        test += api.override_step_data(
            'read test spec (%s)' % test_spec_name,
            api.json.output({
                b: {
                    'gtest_tests': [
                        {
                            'test': 'browser_tests',
                            'swarming': {'can_use_on_swarming_builders': True},
                        },
                    ],
                } for b in builders_with_tests
          })
      )
      yield test

  yield (
    api.test('dynamic_gtest') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
              'gtest_tests': [
                'base_unittests',
                {'test': 'browser_tests', 'shard_index': 0, 'total_shards': 2},
                {
                    'test': 'content_unittests',
                    'name': 'renamed_content_unittests',
                    'use_xvfb': False,
                },
              ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_gtest') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'gtest_tests': [
                    {'test': 'browser_tests',
                     'swarming': {'can_use_on_swarming_builders': True}},
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_serialized_gtests') +
    # The chromium.gpu.fyi bots use serialize_tests in order to reduce
    # load on the GPU bots in the Swarming pool.
    api.properties.generic(mastername='chromium.gpu.fyi',
                           buildername='Linux Release (NVIDIA)',
                           parent_buildername='GPU Linux Builder') +
    api.platform('linux', 64) +
    api.properties(swarm_hashes={
      'base_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
      'browser_tests': 'ffffffffffffffffffffffffffffff',
    }) +
    api.override_step_data(
        'read test spec (chromium.gpu.fyi.json)',
        api.json.output({
            'Linux Release (NVIDIA)': {
                'gtest_tests': [
                    {
                        'test': 'base_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    'gpu': '10de:104a',  # NVIDIA GeForce GT 610
                                    'os': 'Linux',
                                },
                            ],
                        },
                    },
                    {
                        'test': 'browser_tests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    'gpu': '10de:104a',  # NVIDIA GeForce GT 610
                                    'os': 'Linux',
                                },
                            ],
                        },
                    },
                ],
            },
        })
    ) +
    # Make one of the tests fail to improve code coverage.
    api.override_step_data('base_unittests on NVIDIA GPU on Linux on Linux',
        api.test_utils.canned_gtest_output(False))
  )

  yield (
    api.test('dynamic_swarmed_gtest_mac_gpu') +
    api.properties.generic(mastername='chromium.mac',
                           buildername='Mac10.9 Tests',
                           parent_buildername='Mac Builder') +
    api.properties(swarm_hashes={
      'gl_tests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('mac', 64) +
    api.override_step_data(
        'read test spec (chromium.mac.json)',
        api.json.output({
            'Mac10.9 Tests': {
                'gtest_tests': [
                    {
                        'test': 'gl_tests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    'gpu': '8086:0a2e',  # Intel Iris
                                    'hidpi': '0',
                                    'os': 'Mac-10.10',
                                }, {
                                    'gpu': '10de:0fe9',  # NVIDIA GeForce GT750M
                                    'hidpi': '1',
                                    'os': 'Mac-10.9',
                                },
                            ],
                        },
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_gtest_override_compile_targets') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.properties(swarm_hashes={
      'tab_capture_end2end_tests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'gtest_tests': [
                    {
                        'test': 'tab_capture_end2end_tests',
                        'override_compile_targets': [
                            'tab_capture_end2end_tests_run'
                        ],
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                        },
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('build_dynamic_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                      'isolate_name': 'telemetry_gpu_unittests',
                      'name': 'telemetry_gpu_unittests',
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'args': ['--correct-common-arg'],
                        'precommit_args': [
                            '--SHOULD-NOT-BE-PRESENT-DURING-THE-RUN'
                        ],
                        'non_precommit_args': [
                            '--these-args-should-be-present',
                            '--test-machine-name=\"${buildername}\"',
                            '--build-revision=\"${got_revision}\"',
                        ],
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_isolated_script_test_harness_failure_zero_retcode') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                      'isolate_name': 'telemetry_gpu_unittests',
                      'name': 'telemetry_gpu_unittests',
                    },
                ],
            },
        })
    ) +
    api.override_step_data('telemetry_gpu_unittests',
        api.test_utils.canned_isolated_script_output(
            passing=False, is_win=False, swarming=False,
            isolated_script_passing=False, valid=False),
        retcode=0)
  )

  yield (
    api.test('build_dynamic_isolated_script_test_compile_target_overriden') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'override_compile_targets': [
                            'abc',
                            'telemetry_gpu_unittests_run'
                        ],
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('build_dynamic_swarmed_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                      'isolate_name': 'telemetry_gpu_unittests',
                      'name': 'telemetry_gpu_unittests',
                      'swarming': {'can_use_on_swarming_builders': True},
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test(
        'build_dynamic_swarmed_isolated_script_test_compile_target_overidden') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {'can_use_on_swarming_builders': True},
                        'override_compile_targets': [
                            'telemetry_gpu_unittests_run',
                            'a'
                        ],
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_passed_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {'can_use_on_swarming_builders': True},
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_sharded_passed_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'shards': 2,
                        },
                    },
                ],
            },
        })
    ) +
    api.override_step_data('telemetry_gpu_unittests on Ubuntu-12.04',
        api.test_utils.canned_isolated_script_output(
            passing=True, is_win=False, swarming=True,
            shards=2, isolated_script_passing=True, valid=True),
        retcode=0)
  )

  yield (
    api.test('dynamic_swarmed_sharded_failed_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'shards': 2,
                        },
                    },
                ],
            },
        })
    ) +
    api.override_step_data('telemetry_gpu_unittests on Ubuntu-12.04',
        api.test_utils.canned_isolated_script_output(
            passing=False, is_win=False, swarming=True,
            shards=2, isolated_script_passing=False, valid=True),
            retcode=1)
  )

  yield (
    api.test('dynamic_swarmed_sharded_isolated_script_test_missing_shard') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'shards': 2,
                        },
                    },
                ],
            },
        })
    ) +
    api.override_step_data(
      'telemetry_gpu_unittests on Ubuntu-12.04',
      api.test_utils.canned_isolated_script_output(
        passing=True, is_win=False, swarming=True,
        shards=2, isolated_script_passing=True, valid=True,
        missing_shards=[1]),
      retcode=1)
  )

  yield (
    api.test('dynamic_swarmed_sharded_isolated_script_test_harness_failure') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'shards': 2,
                        },
                    },
                ],
            },
        })
    ) +
    api.override_step_data(
      'telemetry_gpu_unittests on Ubuntu-12.04',
      api.test_utils.canned_isolated_script_output(
        passing=True, is_win=False, swarming=True,
        shards=2, isolated_script_passing=True, valid=True,
        empty_shards=[1]),
      retcode=1)
  )

  yield (
    api.test('dynamic_swarmed_isolated_script_test_linux_gpu') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    'gpu': '10de:104a',  # NVIDIA GeForce GT 610
                                    'os': 'Linux',
                                },
                            ],
                        },
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_isolated_script_test_mac_gpu') +
    api.properties.generic(mastername='chromium.mac',
                           buildername='Mac10.9 Tests',
                           parent_buildername='Mac Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('mac', 64) +
    api.override_step_data(
        'read test spec (chromium.mac.json)',
        api.json.output({
            'Mac10.9 Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    'gpu': '8086:0a2e',  # Intel Iris
                                    'hidpi': '0',
                                    'os': 'Mac-10.10',
                                }, {
                                    'gpu': '10de:0fe9',  # NVIDIA GeForce GT750M
                                    'hidpi': '1',
                                    'os': 'Mac-10.9',
                                },
                            ],
                        },
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_isolated_script_test_win_gpu') +
    api.properties.generic(mastername='chromium.win',
                           buildername='Win7 Tests (1)',
                           parent_buildername='Win Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('win', 64) +
    api.override_step_data(
        'read test spec (chromium.win.json)',
        api.json.output({
            'Win7 Tests (1)': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    # NVIDIA GeForce GT 610
                                    'gpu': '10de:104a',
                                    'os': 'Windows',
                                }, {
                                    # AMD Radeon HD 6450
                                    'gpu': '1002:6779',
                                    'os': 'Windows',
                                }, {
                                    # VMWare SVGA II Adapter
                                    'gpu': '15ad:0405',
                                    'os': 'Windows',
                                },
                            ],
                        },
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_isolated_script_test_win_non_gpu') +
    api.properties.generic(mastername='chromium.win',
                           buildername='Win7 Tests (1)',
                           parent_buildername='Win Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('win', 64) +
    api.override_step_data(
        'read test spec (chromium.win.json)',
        api.json.output({
            'Win7 Tests (1)': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                  'os': 'Windows',
                                },
                            ],
                        },
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_failed_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                      'isolate_name': 'telemetry_gpu_unittests',
                      'name': 'telemetry_gpu_unittests',
                      'swarming': {'can_use_on_swarming_builders': True},
                    },
                ],
            },
        })
    ) +
    api.override_step_data('telemetry_gpu_unittests on Ubuntu-12.04',
        api.test_utils.canned_isolated_script_output(
            passing=True, is_win=False, swarming=True,
            isolated_script_passing=False, valid=True),
        retcode=255)
  )

  yield (
    api.test('dynamic_swarmed_passed_with_bad_retcode_isolated_script_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                        'isolate_name': 'telemetry_gpu_unittests',
                        'name': 'telemetry_gpu_unittests',
                        'swarming': {'can_use_on_swarming_builders': True},
                    },
                ],
            },
        })
    ) +
    api.override_step_data('telemetry_gpu_unittests on Ubuntu-12.04',
        api.test_utils.canned_isolated_script_output(
            passing=True, is_win=False, swarming=True,
            isolated_script_passing=True, valid=True),
        retcode=255)
  )

  yield (
    api.test(
        'dynamic_swarmed_passed_isolated_script_test_with_swarming_failure') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.properties(swarm_hashes={
      'telemetry_gpu_unittests': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    }) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'isolated_scripts': [
                    {
                      'isolate_name': 'telemetry_gpu_unittests',
                      'name': 'telemetry_gpu_unittests',
                      'swarming': {'can_use_on_swarming_builders': True},
                    },
                ],
            },
        })
    ) +
    api.override_step_data('telemetry_gpu_unittests on Ubuntu-12.04',
        api.test_utils.canned_isolated_script_output(
            passing=False, is_win=False, swarming=True,
            swarming_internal_failure=True, isolated_script_passing=True,
            valid=True),
        retcode=255)
  )

  yield (
    api.test('dynamic_android_cloud_gtest') +
    api.properties.generic(mastername='chromium.fyi',
                           buildername='Android Cloud Tests') +
    api.override_step_data(
        'read test spec (chromium.fyi.json)',
        api.json.output({
            'Android Cloud Tests': {
                'gtest_tests': [
                    {
                      'args': [
                          '--isolate-file-path=src/base/base_unittests.isolate',
                      ],
                      'test': 'base_unittests',
                    },
                ],
            }
        })
    )
  )

  yield (
    api.test('dynamic_instrumentation_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Android Tests',
                           parent_buildername='Android Builder') +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Android Tests': {
                'instrumentation_tests': [
                    {
                        'test': 'ChromePublicTest',
                        'test_apk': 'one_apk',
                        'apk_under_test': 'second_apk',
                        'additional_apks': [
                            'another_apk',
                            'omg_so_many_apks',
                        ]
                    }
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_instrumentation_nodefault_build') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Android Builder') +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Android Tests': {
                'instrumentation_tests': [
                    {
                        'test': 'blimp_test_apk',
                    }
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_instrumentation_nodefault_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Android Tests',
                           parent_buildername='Android Builder') +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Android Tests': {
                'instrumentation_tests': [
                    {
                        'test': 'blimp_test_apk',
                    }
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_instrumentation_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Android Tests',
                           parent_buildername='Android Builder') +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Android Tests': {
                'instrumentation_tests': [
                    {
                        'test': 'chrome_public_test',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    'build.id': 'KTU84P',
                                    'product.board': 'hammerhead',
                                },
                            ],
                        },
                    }
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_swarmed_gn_instrumentation_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Android Builder') +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Android Tests': {
                'gtest_tests': [
                    {
                        'test': 'chrome_public_test_apk',
                        'swarming': {
                            'can_use_on_swarming_builders': True,
                            'dimension_sets': [
                                {
                                    'build.id': 'KTU84P',
                                    'product.board': 'hammerhead',
                                },
                            ],
                            'cipd_packages': [
                                {
                                    'location': '{$HOME}/logdog',
                                    'cipd_package': 'infra/logdog/linux-386',
                                    'revision': 'git_revision:deadbeef',
                                },
                            ],
                        },
                        'override_compile_targets': [
                            'chrome_public_test_apk'
                         ],
                        'override_isolate_target': 'chrome_public_test_apk',
                    }
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_instrumentation_cloud_test') +
    api.properties.generic(mastername='chromium.fyi',
                           buildername='Android Cloud Tests',
                           parent_buildername='Android Builder') +
    api.override_step_data(
        'read test spec (chromium.fyi.json)',
        api.json.output({
            'Android Cloud Tests': {
                'instrumentation_tests': [
                    {
                        'test': 'ChromePublicTest',
                        'test_apk': 'one_apk',
                        'apk_under_test': 'second_apk',
                        'additional_apks': [
                            'another_apk',
                            'omg_so_many_apks',
                        ]
                    }
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_instrumentation_test_with_timeout_scale') +
    api.properties.generic(mastername='chromium.android',
                           buildername='Lollipop Low-end Tester',
                           parent_buildername='Android arm Builder (dbg)') +
    api.override_step_data(
        'read test spec (chromium.android.json)',
        api.json.output({
            'Lollipop Low-end Tester': {
                'instrumentation_tests': [
                    {
                      'test': 'ChromePublicTest',
                      'timeout_scale': 2,
                    }
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_junit_test') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Android Tests',
                           parent_buildername='Android Builder') +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Android Tests': {
                'junit_tests': [
                    {
                        'test': 'base_junit_tests',
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_gtest_on_builder') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'gtest_tests': [
                    'base_unittests',
                    {
                        'test': 'browser_tests',
                        'shard_index': 0,
                        'total_shards': 2
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_gtest_win') +
    api.properties.generic(mastername='chromium.win',
                           buildername='Win7 Tests (1)',
                           parent_buildername='Win Builder') +
    api.platform('win', 64) +
    api.override_step_data(
        'read test spec (chromium.win.json)',
        api.json.output({
            'Win7 Tests (1)': {
                'gtest_tests': [
                    'aura_unittests',
                    {
                        'test': 'browser_tests',
                        'shard_index': 0,
                        'total_shards': 2
                    },
                ],
            },
        })
    )
  )

  # Tests switching on asan and swiching off lsan for sandbox tester.
  yield (
    api.test('dynamic_gtest_memory_asan_no_lsan') +
    api.properties.generic(mastername='chromium.memory',
                           buildername='Linux ASan Tests (sandboxed)',
                           parent_buildername='Linux ASan LSan Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.memory.json)',
        api.json.output({
            'Linux ASan Tests (sandboxed)': {
                'gtest_tests': [
                    'browser_tests',
                ],
            },
        })
    )
  )

  # Tests that the memory builder is using the correct compile targets.
  yield (
    api.test('dynamic_gtest_memory_builder') +
    api.properties.generic(mastername='chromium.memory',
                           buildername='Linux ASan LSan Builder',
                           revision='123456') +
    api.platform('linux', 64) +
    # The builder should build 'browser_tests', because there exists a child
    # tester that uses that test.
    api.override_step_data(
        'read test spec (chromium.memory.json)',
        api.json.output({
            'Linux ASan Tests (sandboxed)': {
                'gtest_tests': [
                    'browser_tests',
                ],
            },
        })
    )
  )

  # Tests that the memory mac tester is using the correct test flags.
  yield (
    api.test('dynamic_gtest_memory_mac64') +
    api.properties.generic(
        mastername='chromium.memory',
        buildername='Mac ASan 64 Tests (1)',
        parent_buildername='Mac ASan 64 Builder') +
    api.platform('mac', 64) +
    api.override_step_data(
        'read test spec (chromium.memory.json)',
        api.json.output({
            'Mac ASan 64 Tests (1)': {
                'gtest_tests': [
                    'browser_tests',
                ],
            },
        })
    )
  )

  yield (
    api.test('tsan') +
    api.properties.generic(mastername='chromium.memory.fyi',
                           buildername='Linux TSan Tests',
                           parent_buildername='Chromium Linux TSan Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.memory.fyi.json)',
        api.json.output({
            'Linux TSan Tests': {
                'compile_targets': ['base_unittests'],
                'gtest_tests': ['base_unittests'],
            },
        })
    )
  )

  yield (
    api.test('msan') +
    api.properties.generic(mastername='chromium.memory.fyi',
                           buildername='Linux MSan Tests',
                           parent_buildername='Chromium Linux MSan Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.memory.fyi.json)',
        api.json.output({
            'Linux MSan Tests': {
                'compile_targets': ['base_unittests'],
                'gtest_tests': ['base_unittests'],
            },
        })
    )
  )

  yield (
    api.test('buildnumber_zero') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder',
                           buildnumber=0) +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'gtest_tests': [
                    'base_unittests',
                    {
                        'test': 'browser_tests',
                        'shard_index': 0,
                        'total_shards': 2
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('one_failure_keeps_going_dynamic_tests') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'gtest_tests': [
                    'base_unittests',
                    {
                        'test': 'browser_tests',
                        'shard_index': 0,
                        'total_shards': 2
                    },
                ],
            },
        })
    ) +
    api.step_data('base_unittests', retcode=1)
  )

  yield (
    api.test('perf_test_profile_failure') +
    api.properties.generic(mastername='chromium.perf',
                           buildername='Linux Perf (1)',
                           parent_buildername='Linux Builder',
                           buildnumber=0) +
    api.platform('linux', 64) +
    api.override_step_data(
        'blink_perf.all.release',
        api.json.output([]),
        retcode=1)
  )

  yield (
    api.test('dynamic_script_test_with_args') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'scripts': [
                    {
                        'name': 'media_perftests',
                        'script': 'gtest_perf_test.py',
                        'args': ['media_perftests', '--single-process-tests']
                    },
                ],
            },
        })
    )
  )

  yield (
    api.test('dynamic_script_test_failure') +
    api.properties.generic(mastername='chromium.linux',
                           buildername='Linux Tests',
                           parent_buildername='Linux Builder') +
    api.platform('linux', 64) +
    api.override_step_data(
        'read test spec (chromium.linux.json)',
        api.json.output({
            'Linux Tests': {
                'scripts': [
                    {
                      'name': 'test_script_with_broken_tests',
                      'script': 'test_script_with_broken_tests.py'
                    }
                ]
            }
        })
    ) +
    api.override_step_data('test_script_with_broken_tests',
                           api.json.output({
      'valid': True,
      'failures': ['FailSuite.Test1', 'FlakySuite.TestA']
    }))
  )

  yield (
    api.test('chromium_webkit_crash') +
    api.properties.generic(mastername='chromium.webkit',
                           buildername='WebKit Linux') +
    api.platform('linux', 64) +
    api.override_step_data(
        'webkit_tests',
        api.test_utils.raw_test_output(None, retcode=1))
  )

  yield (
    api.test('chromium_webkit_warnings') +
    api.properties.generic(mastername='chromium.webkit',
                           buildername='WebKit Linux') +
    api.platform('linux', 64) +
    api.override_step_data(
        'webkit_tests',
        api.test_utils.canned_test_output(
            passing=True, unexpected_flakes=True, retcode=0))
  )

  yield (
    api.test('chromium_webkit_revision_webkit') +
    api.properties.generic(mastername='chromium.webkit',
                           buildername='WebKit Linux',
                           project='webkit',
                           revision='191187') +
    api.platform('linux', 64)
  )

  yield (
    api.test('chromium_webkit_revision_chromium') +
    api.properties.generic(
        mastername='chromium.webkit',
        buildername='WebKit Linux',
        project='chromium',
        revision='3edb4989f8f69c968c0df14cb1c26d21dd19bf1f') +
    api.platform('linux', 64)
  )

  yield (
    api.test('chromium_webkit_parent_revision_webkit') +
    api.properties.generic(
        mastername='chromium.webkit',
        buildername='WebKit Win7',
        project='webkit',
        parent_buildername='WebKit Win Builder',
        parent_got_revision='7496f63cbefd34b2d791022fbad64a82838a3f3f',
        parent_got_webkit_revision='191275',
        revision='191275') +
    api.platform('win', 32)
  )

  yield (
    api.test('chromium_webkit_parent_revision_chromium') +
    api.properties.generic(
        mastername='chromium.webkit',
        buildername='WebKit Win7',
        project='chromium',
        parent_buildername='WebKit Win Builder',
        parent_got_revision='1e74b372f951d4491f305ec64f6decfcda739e73',
        parent_got_webkit_revision='191269',
        revision='1e74b372f951d4491f305ec64f6decfcda739e73') +
    api.platform('win', 32)
  )

  yield (
    api.test('kitchen_path_config') +
    api.properties(
        mastername='chromium.fyi',
        buildername='Linux remote_run Builder',
        slavename='build1-a1',
        buildnumber='77457',
        path_config='kitchen')
  )

  yield (
    api.test('ensure_goma_fail') +
    api.properties(
        mastername='chromium.fyi',
        buildername='Linux remote_run Builder',
        slavename='build1-a1',
        buildnumber='77457',
        path_config='kitchen') +
    api.override_step_data('ensure_goma.ensure_installed', retcode=1)
  )

# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from . import steps

SPEC = {
  'settings': {
    'build_gs_bucket': 'chromium-mac-archive',
    # WARNING: src-side runtest.py is only tested with chromium CQ builders.
    # Usage not covered by chromium CQ is not supported and can break
    # without notice.
    'src_side_runtest_py': True,
  },
  'builders': {
    'Mac Builder': {
      'chromium_config': 'chromium',
      'chromium_apply_config': [
        'archive_gpu_tests',
        'chrome_with_codecs',
        'mb',
        'ninja_confirm_noop',
        'force_mac_toolchain',
      ],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'compile_targets': [
        'chromium_builder_tests',
      ],
      'testing': {
        'platform': 'mac',
      },
      'enable_swarming': True,
      'use_isolate': True,
      'checkout_dir': 'mac',
    },
    'Mac10.9 Tests': {
      'chromium_config': 'chromium',
      'chromium_apply_config': ['ninja_confirm_noop', 'force_mac_toolchain'],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'bot_type': 'tester',
      'parent_buildername': 'Mac Builder',
      'testing': {
        'platform': 'mac',
      },
      'enable_swarming': True,
      'swarming_dimensions': {
        'os': 'Mac-10.9',
      },
    },
    'Mac10.10 Tests': {
      'chromium_config': 'chromium',
      'chromium_apply_config': ['ninja_confirm_noop', 'force_mac_toolchain'],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'bot_type': 'tester',
      'parent_buildername': 'Mac Builder',
      'testing': {
        'platform': 'mac',
      },
      'swarming_dimensions': {
        'os': 'Mac-10.10',
      },
    },
    'Mac10.11 Tests': {
      'chromium_config': 'chromium',
      'chromium_apply_config': ['ninja_confirm_noop', 'force_mac_toolchain'],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'bot_type': 'tester',
      'parent_buildername': 'Mac Builder',
      'testing': {
        'platform': 'mac',
      },
    },
    'Mac GYP': {
      'chromium_config': 'chromium',
      'chromium_apply_config': ['mb', 'force_mac_toolchain'],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_PLATFORM': 'mac',
      },
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'enable_swarming': True,
      'checkout_dir': 'mac_gyp',
      'testing': {
        'platform': 'mac',
      },
    },
    'Mac Builder (dbg)': {
      'chromium_config': 'chromium',
      'chromium_apply_config': [
        'mb',
        'ninja_confirm_noop',
        'force_mac_toolchain'
      ],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Debug',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'compile_targets': [
        'chromium_builder_tests',
      ],
      'testing': {
        'platform': 'mac',
      },
      'enable_swarming': True,
      'use_isolate': True,
      'checkout_dir': 'mac',
    },
    'Mac10.9 Tests (dbg)': {
      'chromium_config': 'chromium',
      'chromium_apply_config': ['ninja_confirm_noop', 'force_mac_toolchain'],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Debug',
        'TARGET_BITS': 64,
      },
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'bot_type': 'tester',
      'parent_buildername': 'Mac Builder (dbg)',
      'testing': {
        'platform': 'mac',
      },
      'enable_swarming': True,
      'swarming_dimensions': {
        'os': 'Mac-10.9',
      },
    },
    'Mac GYP (dbg)': {
      'chromium_config': 'chromium',
      'chromium_apply_config': ['mb', 'force_mac_toolchain'],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Debug',
        'TARGET_PLATFORM': 'mac',
      },
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'enable_swarming': True,
      'checkout_dir': 'mac_gyp',
      'testing': {
        'platform': 'mac',
      },
    },
  },
}

# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from . import steps

SPEC = {
  'builders': {
    'Win': {
      'chromium_config': 'chromium',
      'chromium_apply_config': [
        'clobber',
        'isolation_mode_noop',
        'mb',
        'ninja_confirm_noop',
        'no_dump_symbols',
      ],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 32,
      },
      'compile_targets': [
        'all',
      ],
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'archive_build': True,
      'gs_bucket': 'chromium-browser-snapshots',
      'gs_acl': 'public-read',
      'checkout_dir': 'win_archive',
      'testing': {
        'platform': 'win',
      },
    },
    'Win x64': {
      'chromium_config': 'chromium',
      'chromium_apply_config': [
        'clobber',
        'isolation_mode_noop',
        'ninja_confirm_noop',
        'no_dump_symbols',
      ],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'compile_targets': [
        'all',
      ],
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'archive_build': True,
      'gs_bucket': 'chromium-browser-snapshots',
      'gs_acl': 'public-read',
      'checkout_dir': 'win_x64_archive',
      'testing': {
        'platform': 'win',
      },
    },
    'Mac': {
      'chromium_config': 'chromium',
      'chromium_apply_config': [
        'clobber',
        'isolation_mode_noop',
        'mb',
        'ninja_confirm_noop',
        'no_dump_symbols',
      ],
      'gclient_config': 'chromium',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'compile_targets': [
        'all',
      ],
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'archive_build': True,
      'gs_bucket': 'chromium-browser-snapshots',
      'gs_acl': 'public-read',
      'checkout_dir': 'mac_ng',
      'testing': {
        'platform': 'mac',
      },
    },
    'Linux x64': {
      'chromium_config': 'chromium',
      'chromium_apply_config': [
        'clobber',
        'isolation_mode_noop',
        'mb',
        'ninja_confirm_noop',
        'no_dump_symbols',
      ],
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
      'archive_build': True,
      'gs_bucket': 'chromium-browser-snapshots',
      'gs_acl': 'public-read',
      'testing': {
        'platform': 'linux',
      },
    },
    'Android': {
      'chromium_config': 'android',
      'chromium_apply_config': [
        'clobber',
        'isolation_mode_noop',
        'mb',
        'no_dump_symbols',
      ],
      'gclient_config': 'chromium',
      'gclient_apply_config': ['android'],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_PLATFORM': 'android',
        'TARGET_ARCH': 'arm',
      },
      'android_config': 'main_builder',
      'compile_targets': [
        'all',
      ],
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'archive_build': True,
      'gs_bucket': 'chromium-browser-snapshots',
      'gs_acl': 'public-read',
      'testing': {
        'platform': 'linux',
      },
    },
  },
}

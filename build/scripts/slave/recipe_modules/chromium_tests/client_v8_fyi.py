# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from . import steps

SPEC = {
  'settings': {
    'build_gs_bucket': 'chromium-v8',
  },
  'builders': {
    'Linux Debug Builder': {
      'chromium_config': 'chromium',
      'gclient_config': 'chromium',
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkcr',
        'show_v8_revision',
      ],
      'chromium_apply_config': ['mb', 'ninja_confirm_noop'],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Debug',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'testing': {
        'platform': 'linux',
        'test_spec_file': 'chromium.linux.json',
      },
    },
    'V8 Linux GN': {
      'chromium_config': 'chromium',
      'gclient_config': 'chromium',
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkcr',
        'show_v8_revision',
      ],
      'chromium_apply_config': ['mb', 'ninja_confirm_noop'],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'compile_targets': [
        'blink_tests',
        'extensions_browsertests',
        'gin_unittests',
        'pdfium_test',
        'postmortem-metadata',
        'net_unittests',
        'unit_tests',
      ],
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'testing': {
        'platform': 'linux',
        'test_spec_file': 'chromium.linux.json',
      },
    },
    'V8 Android GN (dbg)': {
      'chromium_config': 'android',
      'chromium_apply_config': ['mb'],
      'gclient_config': 'chromium',
      'gclient_apply_config': [
        'android',
        'v8_bleeding_edge_git',
        'chromium_lkcr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Debug',
        'TARGET_PLATFORM': 'android',
        'TARGET_ARCH': 'arm',
      },
      'android_config': 'main_builder',
      'bot_type': 'builder',
      'compile_targets': [
        'blink_tests',
        'gin_unittests',
        'net_unittests',
      ],
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'testing': {
        'platform': 'linux',
        'test_spec_file': 'chromium.linux.json',
      },
    },
    # Bot names should be in sync with chromium.linux's names to retrieve the
    # same test configuration files.
    'Linux Tests (dbg)(1)': {
      'chromium_config': 'chromium',
      'gclient_config': 'chromium',
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkcr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Debug',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'parent_buildername': 'Linux Debug Builder',
      'testing': {
        'platform': 'linux',
        'test_spec_file': 'chromium.linux.json',
      },
    },
    'Linux ASAN Builder': {
      'chromium_config': 'chromium_linux_asan',
      'chromium_apply_config': ['mb'],
      'gclient_config': 'chromium',
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkcr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'testing': {
        'platform': 'linux',
        'test_spec_file': 'chromium.memory.json',
      },
    },
    'Linux ASan LSan Tests (1)': {
      'chromium_config': 'chromium_linux_asan',
      'gclient_config': 'chromium',
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkcr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
        steps.generate_isolated_script,
      ],
      'parent_buildername': 'Linux ASAN Builder',
      'testing': {
        'platform': 'linux',
        'test_spec_file': 'chromium.memory.json',
      },
    },
    'Linux Snapshot Builder': {
      'chromium_config': 'chromium',
      'chromium_apply_config': ['mb'],
      'gclient_config': 'chromium',
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkcr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder_tester',
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'tests': [
        steps.ArchiveBuildStep(
            'chromium-v8-snapshots',
            gs_acl='public-read',
        ),
      ],
      'testing': {
        'platform': 'linux',
        'test_spec_file': 'chromium.linux.json',
      },
    },
    # Clusterfuzz builders.
    'Chromium ASAN (symbolized)': {
      'chromium_config': 'chromium_linux_asan',
      'gclient_config': 'chromium',
      'chromium_apply_config': [
        'asan_symbolized',
        'chromium_asan_default_targets',
        'clobber',
        'mb',
        'sanitizer_coverage',
        'v8_verify_heap',
      ],
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkgr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'cf_archive_build': True,
      'cf_gs_bucket': 'v8-asan',
      'cf_gs_acl': 'public-read',
      'cf_archive_name': 'asan-symbolized',
      'cf_revision_dir': 'v8',
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'testing': {'platform': 'linux'},
    },
    'Chromium ASAN - debug': {
      'chromium_config': 'chromium_linux_asan',
      'gclient_config': 'chromium',
      'chromium_apply_config': [
        'chromium_asan_default_targets',
        'clobber',
        'mb',
        'sanitizer_coverage',
        'v8_optimize_medium',
      ],
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkgr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Debug',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'cf_archive_build': True,
      'cf_gs_bucket': 'v8-asan',
      'cf_gs_acl': 'public-read',
      'cf_archive_name': 'asan',
      'cf_revision_dir': 'v8',
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'testing': {'platform': 'linux'},
    },
    'Chromium Win SyzyASAN': {
      'chromium_config': 'chromium_no_goma',
      'gclient_config': 'chromium',
      'chromium_apply_config': ['syzyasan', 'clobber', 'mb'],
      'gclient_apply_config': [
        'v8_bleeding_edge_git',
        'chromium_lkgr',
        'show_v8_revision',
      ],
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 32,
      },
      'bot_type': 'builder',
      'cf_archive_build': True,
      'cf_gs_bucket': 'v8-asan',
      'cf_gs_acl': 'public-read',
      'cf_archive_name': 'syzyasan',
      'cf_revision_dir': 'v8',
      'fixed_staging_dir': True,
      'compile_targets': ['chromium_builder_asan'],
      'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      'testing': {'platform': 'win'},
    },
  },
}

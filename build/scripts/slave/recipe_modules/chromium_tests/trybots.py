# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from recipe_engine.types import freeze


def simple_bot(bot_id, analyze_mode=None):
  return {
    'bot_ids': [bot_id],
    'analyze_mode': analyze_mode,
  }


TRYBOTS = freeze({
  'tryserver.blink': {
    'builders': {
      'linux_blink_dbg': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Linux (dbg)',
      }),
      'linux_blink_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Linux',
      }),
      'linux_blink_compile_dbg': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Linux (dbg)',
      }, analyze_mode='compile'),
      'linux_blink_compile_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Linux',
      }, analyze_mode='compile'),
      'mac_blink_dbg': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Mac10.11 (dbg)',
      }),
      'mac_blink_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Mac10.9',
      }),
      'mac_blink_compile_dbg': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Mac10.11 (dbg)',
      }, analyze_mode='compile'),
      'mac_blink_compile_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Mac10.9',
      }, analyze_mode='compile'),
      'win_blink_dbg': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Win7 (dbg)',
      }),
      'win_blink_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Win7',
      }),
      'win_blink_compile_dbg': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Win7 (dbg)',
      }, analyze_mode='compile'),
      'win_blink_compile_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Win7',
      }, analyze_mode='compile'),
    },
  },
  'tryserver.chromium.android': {
    'builders': {
      'android_archive_rel_ng': simple_bot({
        'mastername': 'chromium',
        'buildername': 'Android',
      }),
      'android_arm64_dbg_recipe': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Android Arm64 Builder (dbg)',
      }, analyze_mode='compile'),
      'android_blink_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Android (Nexus4)',
      }),
      'android_clang_dbg_recipe': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Android Clang Builder (dbg)',
      }, analyze_mode='compile'),
      'android_compile_dbg': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Android Builder (dbg)',
      }, analyze_mode='compile'),
      'android_compile_mips_dbg': simple_bot({
        'mastername': 'chromium.android',
        'buildername': 'Android MIPS Builder (dbg)',
      }, analyze_mode='compile'),
      'android_compile_x64_dbg': simple_bot({
        'mastername': 'chromium.android',
        'buildername': 'Android x64 Builder (dbg)',
      }, analyze_mode='compile'),
      'android_compile_x86_dbg': simple_bot({
        'mastername': 'chromium.android',
        'buildername': 'Android x86 Builder (dbg)',
      }, analyze_mode='compile'),
      'android_compile_rel': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Android Builder',
      }, analyze_mode='compile'),
      'android_coverage': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'Android Coverage (dbg)'
      }),
      'android_n5x_swarming_rel': simple_bot({
        'mastername': 'chromium.android',
        'buildername': 'Android N5X Swarm Builder',
      }),
      'android_optional_gpu_tests_rel': simple_bot({
        'mastername': 'chromium.gpu.fyi',
        'buildername': 'Android Release (Nexus 5X)',
      }),
      'cast_shell_android': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Cast Android (dbg)',
      }),
      'linux_android_dbg_ng': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Android Builder (dbg)',
        'tester': 'Android Tests (dbg)',
      }),
      'linux_android_rel_ng': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Android Builder',
        'tester': 'Android Tests',
      }),
    },
  },
  'tryserver.chromium.angle': {
    'builders': {
      'android_angle_rel_ng': simple_bot({
        'mastername': 'chromium.gpu.fyi',
        'buildername': 'Android Release (Nexus 5X)',
      }),
      'linux_angle_rel_ng': simple_bot({
        'mastername': 'chromium.gpu.fyi',
        'buildername': 'GPU Linux Builder',
        'tester': 'Linux Release (NVIDIA)',
      }),
      'linux_angle_dbg_ng': simple_bot({
        'mastername': 'chromium.gpu.fyi',
        'buildername': 'GPU Linux Builder (dbg)',
        'tester': 'Linux Debug (NVIDIA)',
      }),
      'linux_angle_chromeos_rel_ng': simple_bot({
        'mastername': 'chromium.gpu.fyi',
        'buildername': 'Linux ChromiumOS Builder',
      }),
      'mac_angle_rel_ng': {
        'bot_ids': [
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder',
            'tester': 'Mac 10.10 Release (Intel)',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder',
            'tester': 'Mac Retina Release',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder',
            'tester': 'Mac 10.10 Retina Release (AMD)',
          },
        ],
      },
      'mac_angle_dbg_ng': {
        'bot_ids': [
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder (dbg)',
            'tester': 'Mac 10.10 Debug (Intel)',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder (dbg)',
            'tester': 'Mac Retina Debug',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder (dbg)',
            'tester': 'Mac 10.10 Retina Debug (AMD)',
          },
        ],
      },
      'win_angle_rel_ng': {
        'bot_ids': [
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Win Builder',
            'tester': 'Win7 Release (NVIDIA)',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Win Builder',
            'tester': 'Win7 Release (ATI)',
          },
        ],
      },
      'win_angle_dbg_ng': {
        'bot_ids': [
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Win Builder (dbg)',
            'tester': 'Win7 Debug (NVIDIA)',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Win Builder (dbg)',
            'tester': 'Win7 Debug (ATI)',
          },
        ],
      },
      'win_angle_x64_rel_ng': simple_bot({
        'mastername': 'chromium.gpu.fyi',
        'buildername': 'GPU Win x64 Builder',
        'tester': 'Win7 x64 Release (NVIDIA)',
      }),
      'win_angle_x64_dbg_ng': simple_bot({
        'mastername': 'chromium.gpu.fyi',
        'buildername': 'GPU Win x64 Builder (dbg)',
        'tester': 'Win7 x64 Debug (NVIDIA)',
      }),
    },
  },
  'tryserver.chromium.linux': {
    'builders': {
      'blimp_linux_dbg': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Blimp Linux (dbg)',
      }),
      'cast_shell_linux': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Cast Linux',
      }),
      'linux_arm': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'Linux ARM',
      }),
      'linux_chromium_browser_side_navigation_rel': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'Browser Side Navigation Linux',
      }),
      'linux_chromium_dbg_32_ng': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Linux Builder (dbg)(32)',
        'tester': 'Linux Tests (dbg)(1)(32)',
      }),
      'linux_chromium_dbg_ng': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Linux Builder (dbg)',
        'tester': 'Linux Tests (dbg)(1)',
      }),
      'linux_chromium_gn_chromeos_dbg': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'Linux ChromiumOS GN (dbg)',
      }),
      'linux_chromium_gn_chromeos_rel': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'Linux ChromiumOS GN',
      }),
      'linux_chromium_rel_ng': {
        'bot_ids': [
          {
            'mastername': 'chromium.linux',
            'buildername': 'Linux Builder',
            'tester': 'Linux Tests',
          },
          {
            'mastername': 'chromium.gpu',
            'buildername': 'GPU Linux Builder',
            'tester': 'Linux Release (NVIDIA)',
          },
        ],
      },
      'linux_chromium_asan_rel_ng': simple_bot({
        'mastername': 'chromium.memory',
        'buildername': 'Linux ASan LSan Builder',
        'tester': 'Linux ASan LSan Tests (1)',
      }),
      'linux_chromium_compile_dbg_ng': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Linux Builder (dbg)',
      }, analyze_mode='compile'),
      'linux_chromium_compile_rel_ng': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Linux Builder',
      }, analyze_mode='compile'),
      'linux_chromium_archive_rel_ng': simple_bot({
        'mastername': 'chromium',
        'buildername': 'Linux x64',
      }),
      'linux_chromium_clobber_rel_ng': simple_bot({
        'mastername': 'chromium',
        'buildername': 'Linux x64',
      }, analyze_mode='compile'),
      'linux_chromium_chromeos_dbg_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'Linux ChromiumOS Builder (dbg)',
        'tester': 'Linux ChromiumOS Tests (dbg)(1)',
      }),
      'linux_chromium_chromeos_compile_dbg_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'Linux ChromiumOS Builder (dbg)',
      }, analyze_mode='compile'),
      'linux_chromium_chromeos_rel_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'Linux ChromiumOS Builder',
        'tester': 'Linux ChromiumOS Tests (1)',
      }),
      'linux_chromium_chromeos_asan_rel_ng': simple_bot({
        'mastername': 'chromium.memory',
        'buildername': 'Linux Chromium OS ASan LSan Builder',
        'tester': 'Linux Chromium OS ASan LSan Tests (1)',
      }),
      'chromeos_x86-generic_chromium_compile_only_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'ChromiumOS x86-generic Compile',
      }, analyze_mode='compile'),
      'chromeos_amd64-generic_chromium_compile_only_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'ChromiumOS amd64-generic Compile',
      }, analyze_mode='compile'),
      'chromeos_daisy_chromium_compile_only_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'ChromiumOS daisy Compile',
      }, analyze_mode='compile'),
      'linux_chromium_chromeos_compile_rel_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'Linux ChromiumOS Builder',
      }, analyze_mode='compile'),
      'linux_chromium_chromeos_msan_rel_ng': simple_bot({
        'mastername': 'chromium.memory.fyi',
        'buildername': 'Chromium Linux ChromeOS MSan Builder',
        'tester': 'Linux ChromeOS MSan Tests',
      }),
      'linux_chromium_chromeos_ozone_rel_ng': simple_bot({
        'mastername': 'chromium.chromiumos',
        'buildername': 'Linux ChromiumOS Ozone Builder',
        'tester': 'Linux ChromiumOS Ozone Tests (1)',
      }),
      'linux_chromium_compile_dbg_32_ng': simple_bot({
        'mastername': 'chromium.linux',
        'buildername': 'Linux Builder (dbg)(32)',
      }, analyze_mode='compile'),
      'linux_chromium_msan_rel_ng': simple_bot({
        'mastername': 'chromium.memory.fyi',
        'buildername': 'Chromium Linux MSan Builder',
        'tester': 'Linux MSan Tests',
      }),
      'linux_chromium_tsan_rel_ng': simple_bot({
        'mastername': 'chromium.memory.fyi',
        'buildername': 'Chromium Linux TSan Builder',
        'tester': 'Linux TSan Tests',
      }),
      'linux_chromium_cfi_rel_ng': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'CFI Linux',
      }),
      'linux_site_isolation': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'Site Isolation Linux',
      }),
      # Optional GPU bots.
      'linux_optional_gpu_tests_rel': {
        'bot_ids': [
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Linux Builder',
            'tester': 'Optional Linux Release (NVIDIA)',
          },
        ],
      },
    },
  },
  'tryserver.chromium.mac': {
    'builders': {
      'mac_chromium_archive_rel_ng': simple_bot({
        'mastername': 'chromium',
        'buildername': 'Mac',
      }),
      'mac_chromium_dbg_ng': simple_bot({
        'mastername': 'chromium.mac',
        'buildername': 'Mac Builder (dbg)',
        'tester': 'Mac10.9 Tests (dbg)',
      }),
      'mac_chromium_gyp_dbg': simple_bot({
        'mastername': 'chromium.mac',
        'buildername': 'Mac GYP (dbg)',
      }),
      'mac_chromium_gyp_rel': simple_bot({
        'mastername': 'chromium.mac',
        'buildername': 'Mac GYP',
      }),
      'mac_chromium_rel_ng': {
        'bot_ids': [
          {
            'mastername': 'chromium.mac',
            'buildername': 'Mac Builder',
            'tester': 'Mac10.9 Tests',
          },
          {
            'mastername': 'chromium.gpu',
            'buildername': 'GPU Mac Builder',
            'tester': 'Mac 10.10 Release (Intel)',
          },
          {
            'mastername': 'chromium.gpu',
            'buildername': 'GPU Mac Builder',
            'tester': 'Mac 10.10 Retina Release (AMD)',
          },
        ],
      },
      'mac_chromium_10.10_rel_ng': simple_bot({
        'mastername': 'chromium.mac',
        'buildername': 'Mac Builder',
        'tester': 'Mac10.10 Tests',
      }),
      'mac_chromium_10.10_macviews': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'Chromium Mac 10.10 MacViews',
      }),
      'mac_chromium_compile_dbg_ng': simple_bot({
        'mastername': 'chromium.mac',
        'buildername': 'Mac Builder (dbg)',
      }, analyze_mode='compile'),
      'mac_chromium_compile_rel_ng': simple_bot({
        'mastername': 'chromium.mac',
        'buildername': 'Mac Builder',
      }, analyze_mode='compile'),
      'mac_chromium_asan_rel_ng': simple_bot({
        'mastername': 'chromium.memory',
        'buildername': 'Mac ASan 64 Builder',
        'tester': 'Mac ASan 64 Tests (1)',
      }),
      # Optional GPU bots.
      'mac_optional_gpu_tests_rel': {
        'bot_ids': [
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder',
            'tester': 'Optional Mac 10.10 Release (Intel)',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder',
            'tester': 'Optional Mac Retina Release',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Mac Builder',
            'tester': 'Optional Mac 10.10 Retina Release (AMD)',
          },
        ],
      },
    },
  },
  'tryserver.chromium.win': {
    'builders': {
      'win_archive': simple_bot({
        'mastername': 'chromium',
        'buildername': 'Win',
      }),
      'win_x64_archive': simple_bot({
        'mastername': 'chromium',
        'buildername': 'Win x64',
      }),
      'win_chromium_dbg_ng': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win Builder (dbg)',
        'tester': 'Win7 Tests (dbg)(1)',
      }),
      'win_chromium_rel_ng': {
        'bot_ids': [
          {
            'mastername': 'chromium.win',
            'buildername': 'Win Builder',
            'tester': 'Win7 Tests (1)',
          },
          {
            'mastername': 'chromium.gpu',
            'buildername': 'GPU Win Builder',
            'tester': 'Win7 Release (NVIDIA)',
          },
        ],
      },
      'win10_chromium_x64_rel_ng': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win x64 Builder',
        'tester': 'Win10 Tests x64',
      }),
      'win10_chromium_x64_rel_ng_exp': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win x64 Builder',
        'tester': 'Win10 Tests x64',
      }),
      'win_chromium_compile_dbg_ng': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win Builder (dbg)',
      }, analyze_mode='compile'),
      'win_chromium_compile_rel_ng': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win Builder',
      }, analyze_mode='compile'),
      'win_chromium_x64_rel_ng': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win x64 Builder',
        'tester': 'Win 7 Tests x64 (1)',
      }),
      'win8_chromium_gyp_rel': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win8 GYP',
      }),
      'win8_chromium_gyp_dbg': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'Win8 GYP (dbg)',
      }),
      'win_clang': simple_bot({
        'mastername': 'chromium.win',
        'buildername': 'WinClang64 (dbg)',
      }),
      'win_chromium_syzyasan_rel': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'Win SyzyAsan (rel)',
      }),
      # Experimental clang/win bots.
      'win_clang_dbg': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'CrWinClang(dbg)',
      }),
      'win_clang_rel': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'CrWinClang',
      }),
      'win_clang_x64_dbg': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'CrWinClang64(dbg)',
      }),
      'win_clang_x64_rel': simple_bot({
        'mastername': 'chromium.fyi',
        'buildername': 'CrWinClang64',
      }),
      # Optional GPU bots.
      'win_optional_gpu_tests_rel': {
        'bot_ids': [
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Win Builder',
            'tester': 'Optional Win7 Release (NVIDIA)',
          },
          {
            'mastername': 'chromium.gpu.fyi',
            'buildername': 'GPU Win Builder',
            'tester': 'Win7 Release (ATI)',
          },
        ],
      },
      # Optional Official trybot.
      'win_chrome_official': simple_bot({
        'mastername': 'chromium.chrome',
        'buildername': 'Google Chrome Win',
      }),
    },
  },
  'tryserver.v8': {
    'builders': {
      'v8_linux_blink_rel': simple_bot({
        'mastername': 'chromium.webkit',
        'buildername': 'WebKit Linux',
      }),
      'v8_linux_chromium_gn_rel': simple_bot({
        'mastername': 'client.v8.fyi',
        'buildername': 'V8 Linux GN',
      }),
      'v8_android_chromium_gn_dbg': simple_bot({
        'mastername': 'client.v8.fyi',
        'buildername': 'V8 Android GN (dbg)',
      }),
    },
  },
})

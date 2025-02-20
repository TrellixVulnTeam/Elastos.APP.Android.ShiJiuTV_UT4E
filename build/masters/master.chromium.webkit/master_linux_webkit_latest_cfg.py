# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from master import master_config
from master.factory import remote_run_factory

import master_site_config

ActiveMaster = master_site_config.ChromiumWebkit

defaults = {}

helper = master_config.Helper(defaults)
B = helper.Builder
F = helper.Factory
T = helper.Triggerable


def m_remote_run(recipe, **kwargs):
  return remote_run_factory.RemoteRunFactory(
      active_master=ActiveMaster,
      repository='https://chromium.googlesource.com/chromium/tools/build.git',
      recipe=recipe,
      factory_properties={'path_config': 'kitchen'},
      **kwargs)

defaults['category'] = 'layout'


################################################################################
## Release
################################################################################

#
# Linux Rel Builder/Tester
#
# FIXME: Rename this builder to indicate that it is running precise.
B('WebKit Linux', 'f_webkit_linux_rel', scheduler='global_scheduler')
F('f_webkit_linux_rel', m_remote_run('chromium'))

B('WebKit Linux Trusty', 'f_webkit_linux_rel_trusty',
    scheduler='global_scheduler')
F('f_webkit_linux_rel_trusty', m_remote_run('chromium'))

B('WebKit Linux ASAN', 'f_webkit_linux_rel_asan', scheduler='global_scheduler',
    auto_reboot=True)
F('f_webkit_linux_rel_asan', m_remote_run('chromium'))

B('WebKit Linux MSAN', 'f_webkit_linux_rel_msan', scheduler='global_scheduler',
    auto_reboot=True)
F('f_webkit_linux_rel_msan', m_remote_run('chromium'))

B('WebKit Linux Leak', 'f_webkit_linux_leak_rel', scheduler='global_scheduler',
    category='layout')
F('f_webkit_linux_leak_rel', m_remote_run('chromium'))


################################################################################
## Debug
################################################################################

#
# Linux Dbg Webkit builders/testers
#

B('WebKit Linux (dbg)', 'f_webkit_dbg_tests', scheduler='global_scheduler',
    auto_reboot=True)
F('f_webkit_dbg_tests', m_remote_run('chromium'))


def Update(_config, _active_master, c):
  return helper.Update(c)

# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""ActiveMaster definition."""

from config_bootstrap import Master

class ChromiumOS(Master.ChromiumOSBase):
  project_name = 'ChromiumOS'
  master_port_id = 0
  buildbot_url = 'http://build.chromium.org/p/chromiumos/'

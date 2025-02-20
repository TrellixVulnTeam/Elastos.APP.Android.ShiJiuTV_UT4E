# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from master import master_config
from master.factory import annotator_factory, chromeos_factory

from buildbot.schedulers.basic import SingleBranchScheduler as Scheduler

def Builder(factory_obj, board, gn=False):
  suffix = ''
  if gn:
    suffix = '-gn'

  config = '%s-tot-chromium-pfq-informational%s' % (board, suffix)
  builder = {
      'name': config,
      'builddir': config,
      'category': '2chromium',
      'factory': chromeos_factory.ChromiteRecipeFactory(
          factory_obj, 'cros/cbuildbot'),
      'gatekeeper': 'pfq',
      'scheduler': 'chromium_cros',
      'notify_on_missing': True,
      'properties': {
          'cbb_config': config,
      },
  }
  return builder


def Update(_config, active_master, c):
  factory_obj = annotator_factory.AnnotatorFactory(
      active_master=active_master)

  builders = [
      Builder(factory_obj, 'x86-generic'),
      Builder(factory_obj, 'amd64-generic'),
      Builder(factory_obj, 'daisy'),
      Builder(factory_obj, 'amd64-generic', gn=True),
  ]

  c['schedulers'] += [
      Scheduler(name='chromium_cros',
                branch='master',
                treeStableTimer=60,
                builderNames=[b['name'] for b in builders],
      ),
  ]
  c['builders'] += builders

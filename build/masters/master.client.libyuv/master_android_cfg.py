# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from buildbot.schedulers.basic import SingleBranchScheduler

from master.factory import annotator_factory

m_annotator = annotator_factory.AnnotatorFactory()

def Update(c):
  c['schedulers'].extend([
      SingleBranchScheduler(name='libyuv_android_scheduler',
                            branch='master',
                            treeStableTimer=0,
                            builderNames=[
          'Android Debug',
          'Android Release',
          'Android Debug (GN)',
          'Android Release (GN)',
          'Android Clang Debug',
          'Android ARM64 Debug',
          'Android32 x86 Debug',
          'Android64 x64 Debug',
          'Android32 MIPS Debug',
      ]),
  ])

  specs = [
    {'name': 'Android Debug'},
    {'name': 'Android Release'},
    {'name': 'Android Debug (GN)', 'slavebuilddir': 'android_gn'},
    {'name': 'Android Release (GN)', 'slavebuilddir': 'android_gn'},
    {'name': 'Android Clang Debug', 'slavebuilddir': 'android_clang'},
    {'name': 'Android ARM64 Debug', 'slavebuilddir': 'android_arm64'},
    {'name': 'Android32 x86 Debug', 'slavebuilddir': 'android_x86'},
    {'name': 'Android64 x64 Debug', 'slavebuilddir': 'android_x64'},
    {'name': 'Android32 MIPS Debug', 'slavebuilddir': 'android_mips'},
  ]

  c['builders'].extend([
      {
        'name': spec['name'],
        'factory': m_annotator.BaseFactory('libyuv/libyuv'),
        'notify_on_missing': True,
        'category': 'android',
        'slavebuilddir': spec.get('slavebuilddir', 'android'),
      } for spec in specs
  ])

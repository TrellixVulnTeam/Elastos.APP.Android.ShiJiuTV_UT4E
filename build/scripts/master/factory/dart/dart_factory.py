#!/usr/bin/python
# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Utility class to generate a Dart-specific BuildFactory.

Based on gclient_factory.py.
"""

import random

from buildbot.changes import gitpoller
from buildbot.process.buildstep import RemoteShellCommand
from buildbot.status.mail import MailNotifier
from buildbot.status.status_push import HttpStatusPush
from buildbot.steps import trigger

from common import chromium_utils

from master.factory import chromium_factory
from master.factory.dart import dart_commands
from master.factory.dart.channels import CHANNELS, CHANNELS_BY_NAME
from master.factory import gclient_factory
from master import gitiles_poller
from master import master_utils

import config

android_tools_rev = '@b12d410c0ee23385da78e6c9f353d28fd992e0bd'
android_resources_rev = '@3855'

chromium_git = 'http://git.chromium.org/git/'

dartium_url = config.Master.dart_bleeding + '/deps/dartium.deps'
android_tools_url = chromium_git + 'android_tools.git' + android_tools_rev

github_mirror = 'https://chromium.googlesource.com/external/github.com'
dart_sdk_mirror = github_mirror + '/dart-lang/sdk.git'

if config.Master.v8_internal_url:
  android_resources_url = (config.Master.v8_internal_url +
      '/buildbot_deps/android_testing_resources' + android_resources_rev)
else:
  android_resources_url = None


# We set these paths relative to the dart root, the scripts need to
# fix these to be absolute if they don't run from there.
linux_env = {}
linux_clang_env = {'CC': 'third_party/clang/linux/bin/clang',
                   'CXX': 'third_party/clang/linux/bin/clang++'}
clang_asan = 'third_party/clang/linux/bin/clang++ -fsanitize=address -fPIC'
linux_asan_env_64 = {'CXX': clang_asan,
                     'ASAN_OPTIONS':
                     'handle_segv=0:detect_stack_use_after_return=1'}
linux_asan_env_32 = {'CXX': clang_asan,
                     'ASAN_OPTIONS':
                     'handle_segv=0:detect_stack_use_after_return=0'}

windows_env = {'LOGONSERVER': '\\\\AD1'}

# gclient custom vars
CUSTOM_VARS_SOURCEFORGE_URL = ('sourceforge_url', config.Master.sourceforge_url)
CUSTOM_VARS_GOOGLECODE_URL = ('googlecode_url', config.Master.googlecode_url)
CUSTOM_VARS_CHROMIUM_URL = (
  'chromium_url', config.Master.server_url + config.Master.repo_root)
CUSTOM_VARS_DARTIUM_BASE = ('dartium_base', config.Master.server_url)

custom_vars_list = [CUSTOM_VARS_SOURCEFORGE_URL,
                    CUSTOM_VARS_GOOGLECODE_URL,
                    CUSTOM_VARS_CHROMIUM_URL,
                    CUSTOM_VARS_DARTIUM_BASE]

# gclient custom deps
if config.Master.trunk_internal_url:
  CUSTOM_DEPS_WIN7_SDK = (
    "src/third_party/platformsdk_win7",
    config.Master.trunk_internal_url + "/third_party/platformsdk_win7@23175")
  CUSTOM_DEPS_WIN8_SDK = (
    "src/third_party/platformsdk_win8",
    config.Master.trunk_internal_url
    + "/third_party/platformsdk_win8_9200@32005")
  CUSTOM_DEPS_DIRECTX_SDK = (
    "src/third_party/directxsdk",
    config.Master.trunk_internal_url + "/third_party/directxsdk@20250")
  custom_deps_list_win = [CUSTOM_DEPS_WIN7_SDK,
                          CUSTOM_DEPS_WIN8_SDK,
                          CUSTOM_DEPS_DIRECTX_SDK]
  CUSTOM_DEPS_JAVA = ('dart/third_party/java',
                      config.Master.trunk_internal_url +
                      '/third_party/openjdk')
  # Fix broken ubuntu OpenJDK by importing windows TZ files
  CUSTOM_TZ = ('dart/third_party/java/linux/j2sdk/jre/lib/zi',
               config.Master.trunk_internal_url +
               '/third_party/openjdk/windows/j2sdk/jre/lib/zi')
else:
  custom_deps_list_win = []

# Wix custom deps
if config.Master.trunk_internal_url:
  custom_wix_deps = [(
    'dart/third_party/wix',
    config.Master.trunk_internal_url + "/third_party/wix/v3_6_3303")]
else:
  custom_wix_deps = []

custom_deps_list_chromeOnAndroid = [
    ('dart/third_party/android_tools', android_tools_url),
]
if android_resources_url:
  custom_deps_list_chromeOnAndroid.append(
      ('dart/third_party/android_testing_resources', android_resources_url))

def BuildChromiumFactory(channel, target_platform='win32'):
  def new_solution(deps_url, custom_vars, custom_deps, custom_deps_file, name):
    return  gclient_factory.GClientSolution(
        deps_url,
        name=name,
        custom_vars_list=custom_vars,
        custom_deps_list=custom_deps,
        custom_deps_file=custom_deps_file)

  class DartiumFactory(chromium_factory.ChromiumFactory):
    def __init__(self, target_platform=None):
      if target_platform in ['linux2', 'darwin']:
        # We use make/ninja on our linux/mac dartium builders which use
        # 'src/out' as build directory
        build_directory = 'src/out'
      else:
        # On windows we still use msvc which uses 'src/build' as build directory
        build_directory = 'src/build'
      chromium_factory.ChromiumFactory.__init__(self,
                                                build_directory,
                                                target_platform)
      self._solutions = []

    def add_solution(self, solution):
      self._solutions.append(solution)

  factory = DartiumFactory(target_platform)
  custom_deps_file = 'tools/deps/dartium.deps/DEPS'
  name = 'src/dart'
  deps_url = dart_sdk_mirror
  if target_platform == 'win32':
    factory.add_solution(
        new_solution(deps_url, custom_vars_list, custom_deps_list_win,
                     custom_deps_file, name))
  else:
    factory.add_solution(new_solution(deps_url, custom_vars_list, [],
                                      custom_deps_file, name))

  return factory.ChromiumFactory

def AddGeneralGClientProperties(factory_properties):
  """Adds the general gclient options to ensure we get the correct revisions"""
  # Make sure that pulled in projects have the right revision based on date.
  factory_properties['gclient_transitive'] = True
  # Don't set branch part on the --revision flag - we don't use standard
  # chromium layout and hence this is doing the wrong thing.
  factory_properties['no_gclient_branch'] = True

class DartFactory(gclient_factory.GClientFactory):
  """Encapsulates data and methods common to the dart master.cfg files."""

  DEFAULT_TARGET_PLATFORM = config.Master.default_platform

  # A map used to skip dependencies when a test is not run.
  # The map key is the test name. The map value is an array containing the
  # dependencies that are not needed when this test is not run.
  NEEDED_COMPONENTS = {
  }

  NEEDED_COMPONENTS_INTERNAL = {
  }

  def __init__(self, channel=None, build_dir='sdk', target_platform='posix',
               target_os=None, custom_deps_list=None,
               nohooks_on_update=False, is_standalone=False):
    solutions = []
    self.target_platform = target_platform

    # Default to the bleeding_edge channel
    if not channel:
      channel = CHANNELS_BY_NAME['be']
    self.channel = channel

    deps_url = dart_sdk_mirror

    if not custom_deps_list:
      custom_deps_list = []

    main = gclient_factory.GClientSolution(
        deps_url,
        needed_components=self.NEEDED_COMPONENTS,
        custom_deps_list=custom_deps_list,
        custom_vars_list=custom_vars_list)
    solutions.append(main)

    gclient_factory.GClientFactory.__init__(self, build_dir, solutions,
                                            target_platform=target_platform,
                                            target_os=target_os,
                                            nohooks_on_update=nohooks_on_update)

  def DartFactory(self, target='Release', clobber=False, tests=None,
                  slave_type='BuilderTester', options=None,
                  compile_timeout=1200, build_url=None,
                  factory_properties=None, env=None, triggers=()):
    factory_properties = factory_properties or {}
    AddGeneralGClientProperties(factory_properties)
    tests = tests or []
    gclient_spec = self.BuildGClientSpec(tests)
    # Initialize the factory with the basic steps.
    factory = self.BaseFactory(gclient_spec,
                               factory_properties=factory_properties)
    # Get the factory command object to create new steps to the factory.
    dart_cmd_obj = dart_commands.DartCommands(factory,
                                              target,
                                              self._build_dir,
                                              self.target_platform,
                                              env=env)

    dart_cmd_obj.AddKillStep(step_name="Taskkill before running")

    # We must always add the MaybeClobberStep, since this factory is
    # created at master start, but the choice of clobber or not may be
    # chosen at runtime (e.g. check the 'clobber' box).
    dart_cmd_obj.AddMaybeClobberStep(clobber, options=options)

    # Add the compile step if needed.
    if slave_type in ['BuilderTester', 'Builder', 'Trybot']:
      dart_cmd_obj.AddCompileStep(options=options,
                                  timeout=compile_timeout)

    # Add all the tests.
    if slave_type in ['BuilderTester', 'Trybot', 'Tester']:
      dart_cmd_obj.AddTests(options=options, channel=self.channel)

     # Archive crash dumps
    if slave_type in ['BuilderTester', 'Trybot', 'Tester']:
      # Currently we only do this on bleeding since scripts have not landed
      # on trunk/stable yet.
      if self.channel.name == 'be':
        dart_cmd_obj.AddArchiveCoredumps(options=options)

    for trigger_instance in triggers:
      dart_cmd_obj.AddTrigger(trigger_instance)

    dart_cmd_obj.AddKillStep(step_name="Taskkill after running")

    return factory

  def DartAnnotatedFactory(self, python_script,
                           target='Release', tests=None,
                           timeout=1200, factory_properties=None,
                           env=None, triggers=(), secondAnnotatedRun=False):
    factory_properties = factory_properties or {}
    AddGeneralGClientProperties(factory_properties)

    tests = tests or []
    # Create the spec for the solutions
    gclient_spec = self.BuildGClientSpec(tests)
    # Initialize the factory with the basic steps.
    factory = self.BaseFactory(gclient_spec,
                               factory_properties=factory_properties)
    # Get the factory command object to create new steps to the factory.
    dart_cmd_obj = dart_commands.DartCommands(factory,
                                              target,
                                              self._build_dir,
                                              self._target_platform,
                                              env=env)
    dart_cmd_obj.AddKillStep(step_name="Taskkill before running")

    dart_cmd_obj.AddAnnotatedSteps(python_script, timeout=timeout)

    for trigger_instance in triggers:
      dart_cmd_obj.AddTrigger(trigger_instance)

    if secondAnnotatedRun:
      dart_cmd_obj.AddAnnotatedSteps(python_script, timeout=timeout, run=2)

    dart_cmd_obj.AddKillStep(step_name="Taskkill after running")

    return factory


class PackageFactory(gclient_factory.GClientFactory):
  def __init__(self, build_dir='dart', target_platform='posix',
               extra_deps=None, deps_file=None, java=False):
    self.target_platform = target_platform
    self._build_dir = build_dir
    deps_url = deps_file or 'https://github.com/dart-lang/package-bots.git'
    extra_deps = extra_deps or []
    custom_deps_list = extra_deps
    if config.Master.trunk_internal_url and java:
      custom_deps_list.append(CUSTOM_DEPS_JAVA)
      custom_deps_list.append(CUSTOM_TZ)

    main = gclient_factory.GClientSolution(deps_url,
                                           custom_deps_list=custom_deps_list)
    gclient_factory.GClientFactory.__init__(self, build_dir, [main],
                                            target_platform=target_platform)

  def PackagesAnnotatedFactory(self, python_script, target='Release',
                               env=None, factory_properties=None,
                               trigger_schedulers=None):
    factory_properties = factory_properties or {}
    factory_properties['no_gclient_revision'] = True
    AddGeneralGClientProperties(factory_properties)
    # Create the spec for the solutions
    gclient_spec = self.BuildGClientSpec()

    factory = self.BaseFactory(gclient_spec,
                               factory_properties=factory_properties)
    # Get the factory command object to create new steps to the factory.
    dart_cmd_obj = dart_commands.DartCommands(factory,
                                              target,
                                              self._build_dir,
                                              self.target_platform,
                                              env=env)
    dart_cmd_obj.AddKillStep(step_name="Taskkill before running")
    dart_cmd_obj.AddAnnotatedSteps(python_script)
    dart_cmd_obj.AddKillStep(step_name="Taskkill after running")

    if trigger_schedulers:
      dart_cmd_obj.AddTrigger(trigger.Trigger(
          schedulerNames=trigger_schedulers,
          waitForFinish=False,
          updateSourceStamp=False))

    return factory


class DartUtils(object):
  mac_options = ['--compiler=goma', 'dartium_builder']
  linux_options = ['--compiler=goma', 'dartium_builder']
  win_options = ['dartium_builder']


  win_rel_factory_properties = {
    'gclient_env': {
      'GYP_DEFINES': 'fastbuild=1',
    },
    'gclient_transitive': True,
    'no_gclient_branch': True,
    'gclient_timeout': 3600,
    'annotated_script': 'dart_buildbot_run.py',
  }
  win_rel_factory_properties_ninja = {
    'gclient_env': {
      'GYP_DEFINES': 'fastbuild=1',
      'GYP_GENERATORS': 'ninja',
    },
    'gclient_transitive': True,
    'no_gclient_branch': True,
    'gclient_timeout': 3600,
    'annotated_script': 'dart_buildbot_run.py',
  }

  win_dbg_factory_properties = {
    'gclient_env': {
      # We currently cannot use 'component=shared_library' here, because
      # dartium/src/build/common.gypi will enable 'ExceptionHandling'.
      # This results in the VisualStudio compiler switch '/EHsc' which in turn
      # will unwind the stack and call destructors when doing a longjmp().
      # The DartVM uses it's own mechanism for calling the destructors (see
      # vm/longjump.cc). (i.e. with /EHsc the destructors will be called twice)
      'GYP_DEFINES': 'fastbuild=1 component=static_library',
    },
    'gclient_transitive': True,
    'gclient_timeout': 3600,
    'no_gclient_branch': True,
    'annotated_script': 'dart_buildbot_run.py',
  }
  mac_factory_properties = {
    'gclient_transitive': True,
    'no_gclient_branch': True,
    'gclient_timeout': 3600,
    'annotated_script': 'dart_buildbot_run.py',
  }
  linux_factory_properties = {
    'gclient_env': {
        'GYP_GENERATORS' : 'ninja',
    },
    'gclient_timeout': 3600,
    'gclient_transitive': True,
    'no_gclient_branch': True,
    'annotated_script': 'dart_buildbot_run.py',
  }
  linux32_factory_properties = {
    'gclient_env': {
        'GYP_GENERATORS' : 'ninja',
        'GYP_DEFINES': 'target_arch=ia32',
    },
    'gclient_timeout': 3600,
    'gclient_transitive': True,
    'no_gclient_branch': True,
    'annotated_script': 'dart_buildbot_run.py',
  }

  @staticmethod
  def get_factory_base(channel):
    postfix = channel.builder_postfix
    factory_base = {
      'posix' + postfix: DartFactory(channel),
      'posix-standalone' + postfix: DartFactory(channel, is_standalone=True),
      'posix-standalone-noRunhooks' + postfix:
          DartFactory(channel, nohooks_on_update=True, is_standalone=True),
      'chromeOnAndroid' + postfix:
          DartFactory(channel,
                      custom_deps_list=custom_deps_list_chromeOnAndroid),
      'android' + postfix: DartFactory(channel, target_os='android'),
      'windows' + postfix: DartFactory(channel, target_platform='win32'),
      'windows-wix' + postfix:
          DartFactory(channel, target_platform='win32',
                      custom_deps_list=custom_wix_deps),
    }
    return factory_base

  @staticmethod
  def get_dartium_factory_base(channel):
    postfix = channel.builder_postfix

    F_MAC_CH = BuildChromiumFactory(channel, target_platform='darwin')
    F_LINUX_CH = BuildChromiumFactory(channel, target_platform='linux2')
    F_WIN_CH = BuildChromiumFactory(channel, target_platform='win32')

    factory_base_dartium = {
      'dartium-mac-full' + postfix: F_MAC_CH(
          target='Release',
          options=DartUtils.mac_options,
          clobber=True,
          tests=['annotated_steps'],
          factory_properties=DartUtils.mac_factory_properties),
      'dartium-mac-inc' + postfix: F_MAC_CH(
          target='Release',
          options=DartUtils.mac_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.mac_factory_properties),
      'dartium-mac-debug' + postfix: F_MAC_CH(
          target='Debug',
          compile_timeout=3600,
          options=DartUtils.mac_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.mac_factory_properties),
      'dartium-lucid64-full' + postfix: F_LINUX_CH(
          target='Release',
          clobber=True,
          options=DartUtils.linux_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.linux_factory_properties),
      'dartium-lucid64-inc' + postfix: F_LINUX_CH(
          target='Release',
          options=DartUtils.linux_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.linux_factory_properties),
      'dartium-lucid64-debug' + postfix: F_LINUX_CH(
          target='Debug',
          options=DartUtils.linux_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.linux_factory_properties),
      'dartium-win-full' + postfix: F_WIN_CH(
          target='Release',
          options=DartUtils.win_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.win_rel_factory_properties),
      'dartium-win-inc' + postfix: F_WIN_CH(
          target='Release',
          options=DartUtils.win_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.win_rel_factory_properties),
      'dartium-win-inc-ninja' + postfix: F_WIN_CH(
          target='Release',
          options=DartUtils.win_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.win_rel_factory_properties_ninja),
      'dartium-win-debug' + postfix: F_WIN_CH(
          target='Debug',
          options=DartUtils.win_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.win_dbg_factory_properties),
      'dartium-lucid32-full' + postfix: F_LINUX_CH(
          target='Release',
          clobber=True,
          options=DartUtils.linux_options,
          tests=['annotated_steps'],
          factory_properties=DartUtils.linux32_factory_properties),
    }
    return factory_base_dartium

  factory_base = {}
  factory_base_dartium = {}

  def __init__(self, active_master):
    self._active_master = active_master

    for channel in CHANNELS:
      DartUtils.factory_base.update(DartUtils.get_factory_base(channel))
    for channel in CHANNELS:
      DartUtils.factory_base_dartium.update(
          DartUtils.get_dartium_factory_base(channel))

  @staticmethod
  def monkey_patch_remoteshell():
    # Hack to increase timeout for steps, dart2js debug checked mode takes more
    # than 8 hours.
    RemoteShellCommand.__init__.im_func.func_defaults = (None,
                                                         1,
                                                         1,
                                                         1200,
                                                         48*60*60, {},
                                                         'slave-config',
                                                         True)

  @staticmethod
  def get_git_poller(repo, project, name, revlink, branch=None, master=None,
                     interval=None, hostid=None):
    changesource_project = '%s-%s' % (name, branch) if branch else name

    hostid = hostid or 'github'
    branch = branch or 'master'
    master = master or 'main'
    interval = interval or 40
    workdir = '/tmp/git_workdir_%s_%s_%s_%s' % (
        hostid, project, changesource_project, master)
    return gitpoller.GitPoller(repourl=repo,
                               pollinterval=interval,
                               project=changesource_project,
                               branch=branch,
                               workdir=workdir,
                               revlinktmpl=revlink)

  @staticmethod
  def get_github_gclient_repo(project, name, branch=None):
    repo = DartUtils.get_github_repo(project, name)
    if branch:
      repo = '%s@refs/remotes/origin/%s' % (repo, branch)
    return repo

  @staticmethod
  def get_github_repo(project, name):
    return 'https://github.com/%s/%s.git' % (project, name)

  @staticmethod
  def get_github_poller(project, name, branch=None, master=None, interval=None):
    repository = 'https://github.com/%s/%s.git' % (project, name)
    revlink = ('https://github.com/' + project + '/' + name + '/commit/%s')
    return DartUtils.get_git_poller(
        repository, project, name, revlink, branch, master, interval=interval,
        hostid='github')

  @staticmethod
  def get_github_mirror_poller(project, name, branch=None, master=None):
    repository = '%s/%s/%s.git' % (github_mirror, project, name)
    revlink = ('https://github.com/' + project + '/' + name + '/commit/%s')
    return DartUtils.get_git_poller(
        repository, project, name, revlink, branch, master,
        hostid='github_mirror')

  @staticmethod
  def prioritize_builders(buildmaster, builders):
    def get_priority(name):
      for channel in CHANNELS:
        if name.endswith(channel.builder_postfix):
          return channel.priority
      # Default to a low priority
      return 10
    # Python's sort is stable, which means that builders with the same priority
    # will be in random order.
    random.shuffle(builders)
    builders.sort(key=lambda b: get_priority(b.name))
    return builders


  def setup_factories(self, variants):
    def setup_dart_factory(v, base, no_annotated):
      # If we have triggers specified, create corresponding trigger.Trigger
      # steps. Example of a trigger specification
      # 'triggers' : [{
      #   'schedulerNames': ['scheduler-arm'],
      #   'waitForFinish': False,
      #   'updateSourceStamp': False,
      # }],
      triggers = v.get('triggers', ())
      trigger_instances = []
      for trigger_spec in triggers:
        trigger_instances.append(
            trigger.Trigger(
                schedulerNames=trigger_spec['schedulerNames'],
                waitForFinish=trigger_spec['waitForFinish'],
                updateSourceStamp=trigger_spec['updateSourceStamp']))

      env = v.get('env', {})
      if no_annotated:
        options = {
            'mode': v['mode'],
            'arch': v['arch'],
            'name': v['name'],
            'vm_options': v.get('vm_options', None),
            'checked_config': v.get('checked_config', None),
        }
        if 'shards' in v and 'shard' in v:
          options['shards'] = v['shards']
          options['shard'] = v['shard']
        v['factory_builder'] = base.DartFactory(
            slave_type='BuilderTester',
            clobber=False,
            options=options,
            env=env,
            triggers=trigger_instances,
        )
      elif v['name'].startswith('packages'):
        v['factory_builder'] = base.PackagesAnnotatedFactory(
            python_script='third_party/package-bots/annotated_steps.py',
            env=env
        )
      else:
        v['factory_builder'] = base.DartAnnotatedFactory(
            python_script='client/tools/buildbot_annotated_steps.py',
            env=env,
            triggers=trigger_instances,
            secondAnnotatedRun=v.get('second_annotated_steps_run', False)
        )

    def setup_package_factory_base(v):
      extra_deps = v.get('deps', [])
      target_platform = 'win32' if v.get('os', '') == 'windows' else 'posix'
      return PackageFactory(extra_deps=extra_deps,
                            target_platform=target_platform)

    for v in variants:
      platform = v['platform']
      if platform == 'packages':
        base = setup_package_factory_base(v)
        setup_dart_factory(v, base, False)
      else:
        base = self.factory_base[platform]
        name = v['name']
        no_annotated = ((name.startswith('vm') or
                        name.startswith('new_analyzer') or
                        name.startswith('analyzer_experimental'))
                        and not name.startswith('vm-android')
                        and not name.startswith('cross-')
                        and not name.startswith('target-'))
        setup_dart_factory(v, base, no_annotated)

  def setup_dartium_factories(self, dartium_variants):
    for variant in dartium_variants:
      name = variant['name']
      variant['factory_builder'] = self.factory_base_dartium[name]

  def get_web_statuses(self, order_console_by_time=True,
                       extra_templates=None):
    public_html = '../master.chromium/public_html'
    templates = ['../master.client.dart/templates',
                 '../master.chromium/templates']
    if extra_templates:
      templates = extra_templates + templates
    master_port = self._active_master.master_port
    master_port_alt = self._active_master.master_port_alt
    kwargs = {
      'public_html' : public_html,
      'templates' : templates,
      'order_console_by_time' : order_console_by_time,
    }

    statuses = []
    statuses.append(master_utils.CreateWebStatus(master_port,
                                                 allowForce=True,
                                                 **kwargs))
    statuses.append(
        master_utils.CreateWebStatus(master_port_alt, allowForce=False,
                                     **kwargs))

    http_status_push_url = self._active_master.http_status_push_url
    if self._active_master.is_production_host and http_status_push_url:
      statuses.append(HttpStatusPush(serverUrl=http_status_push_url))
    return statuses

  @staticmethod
  def get_builders_from_variants(variants,
                                 slaves,
                                 slave_locks,
                                 auto_reboot=False):
    builders = []
    for v in variants:
      builder = {
         'name': v['name'],
         'builddir': v.get('builddir', v['name']),
         'factory': v['factory_builder'],
         'slavenames': slaves.GetSlavesName(builder=v['name']),
         'category': v['category'],
         'locks': slave_locks,
         'auto_reboot': v.get('auto_reboot', auto_reboot)}
      if 'merge_requests' in v:
        builder['mergeRequests'] = v['merge_requests']
      builders.append(builder)
    return builders

  @staticmethod
  def get_builder_names(variants):
    return [variant['name'] for variant in variants]

  @staticmethod
  def get_slaves(builders):
    # The 'slaves' list defines the set of allowable buildslaves. List all the
    # slaves registered to a builder. Remove dupes.
    return master_utils.AutoSetupSlaves(builders,
                                        config.Master.GetBotPassword())

  def get_mail_notifier_statuses(self, mail_notifiers):
    statuses = []
    for mail_notifier in mail_notifiers:
      notifying_builders = mail_notifier['builders']
      extra_recipients = mail_notifier['extraRecipients']
      send_to_interested_useres = mail_notifier.get('sendToInterestedUsers',
                                                    False)
      subject = mail_notifier.get('subject')
      if subject:
        statuses.append(
            MailNotifier(fromaddr=self._active_master.from_address,
                         mode='problem',
                         subject=subject,
                         sendToInterestedUsers=send_to_interested_useres,
                         extraRecipients=extra_recipients,
                         lookup=master_utils.UsersAreEmails(),
                         builders=notifying_builders))
      else:
        statuses.append(
            MailNotifier(fromaddr=self._active_master.from_address,
                         mode='problem',
                         sendToInterestedUsers=send_to_interested_useres,
                         extraRecipients=extra_recipients,
                         lookup=master_utils.UsersAreEmails(),
                         builders=notifying_builders))
    return statuses

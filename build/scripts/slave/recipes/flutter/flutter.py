# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import contextlib

DEPS = [
  'depot_tools/git',
  'file',
  'gsutil',
  'recipe_engine/json',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
  'recipe_engine/step',
  'recipe_engine/python',
]

BUCKET_NAME = 'flutter_infra'


def GetCloudPath(api, git_hash, path):
  return 'flutter/%s/%s' % (git_hash, path)


def TestCreateAndLaunch(api):
  with MakeTempDir(api) as temp_dir:
    api.step('shutdown simulator', ['killall', 'Simulator'], cwd=temp_dir)
    api.step('erase simulator', ['/usr/bin/xcrun', 'simctl', 'erase', 'all'],
        cwd=temp_dir)
    api.step('test create', ['flutter', 'create', '--with-driver-test',
        'sample_app'], cwd=temp_dir)
    app_path = temp_dir.join('sample_app')
    api.step('drive sample_app', ['flutter', 'drive', '--verbose'],
        cwd=app_path)

# TODO(eseidel): Would be nice to have this on api.path or api.file.
@contextlib.contextmanager
def MakeTempDir(api):
  try:
    temp_dir = api.path.mkdtemp('tmp')
    yield temp_dir
  finally:
    api.file.rmtree('temp dir', temp_dir)


def GenerateDocs(api):
  checkout = api.path['checkout']
  api.step('dartdoc packages', ['dev/bots/docs.sh', '--upload'], cwd=checkout)


def BuildExamples(api, git_hash):
  def BuildAndArchive(api, app_dir, apk_name):
    app_path = api.path['checkout'].join(app_dir)
    api.step('flutter build apk %s' % api.path.basename(app_dir),
        ['flutter', 'build', 'apk'], cwd=app_path)

    if api.platform.is_mac:
      app_name = api.path.basename(app_dir)
      # Disable codesigning since this bot has no developer cert.
      api.step('flutter build ios %s' % app_name,
        ['flutter', 'build', 'ios', '--no-codesign'], cwd=app_path)
      api.step('flutter build ios simulator %s' % app_name,
        ['flutter', 'build', 'ios', '--simulator'], cwd=app_path)

    # This is linux just to have only one bot archive at once.
    if api.platform.is_linux:
      cloud_path = GetCloudPath(api, git_hash, 'examples/%s' % apk_name)
      api.gsutil.upload(app_path.join('build/app.apk'), BUCKET_NAME, cloud_path,
          link_name=apk_name, name='upload %s' % apk_name)

  # TODO(eseidel): We should not have to hard-code the desired apk name here.
  BuildAndArchive(api, 'examples/stocks', 'Stocks.apk')
  BuildAndArchive(api, 'examples/flutter_gallery', 'Gallery.apk')


def RunFindXcode(api, step_name, target_version=None):
  """Runs the `build/scripts/slave/ios/find_xcode.py` utility.

     Retrieves information about xcode installations and to activate a specific
     version of Xcode.
  """
  args = ['--json-file', api.json.output()]

  if target_version is not None:
    args.extend(['--version', target_version])

  result = api.python(step_name, api.path['build'].join('scripts', 'slave',
    'ios', 'find_xcode.py'), args)

  return result.json.output


def SetupXcode(api):
  xcode_json = RunFindXcode(api, 'enumerate_xcode_installations')
  installations = xcode_json["installations"]
  activate_version = None
  for key in installations:
    version = installations[key].split()[0]
    if version.startswith('7.'):
      activate_version = version
      break
  if not activate_version:
    raise api.step.StepFailure('Xcode version 7 or above not found')
  RunFindXcode(api, 'set_xcode_version', target_version=activate_version)


def RunSteps(api):
  # buildbot sets 'clobber' to the empty string which is falsey, check with 'in'
  if 'clobber' in api.properties:
    api.file.rmcontents('everything', api.path['slave_build'])

  git_hash = api.git.checkout(
      'https://chromium.googlesource.com/external/github.com/flutter/flutter',
      recursive=True, set_got_revision=True)
  checkout = api.path['checkout']

  api.step('download android tools',
      [checkout.join('dev', 'bots', 'download_android_tools.py')])

  dart_bin = checkout.join('bin', 'cache', 'dart-sdk', 'bin')
  flutter_bin = checkout.join('bin')
  # TODO(eseidel): This is named exactly '.pub-cache' as a hack around
  # a regexp in flutter_tools analyze.dart which is in turn a hack around:
  # https://github.com/dart-lang/sdk/issues/25722
  pub_cache = api.path['slave_build'].join('.pub-cache')
  env = {
    'PATH': api.path.pathsep.join((str(flutter_bin), str(dart_bin),
        '%(PATH)s')),
    # Setup our own pub_cache to not affect other slaves on this machine.
    'PUB_CACHE': pub_cache,
    'ANDROID_HOME': checkout.join('dev', 'bots', 'android_tools'),
  }

  # The context adds dart-sdk tools to PATH sets PUB_CACHE.
  with api.step.context({'env': env}):
    if api.platform.is_mac:
      SetupXcode(api)

    api.step('setup.sh', ['dev/bots/setup.sh'], cwd=checkout)

    if api.platform.is_linux:
      api.step('test.sh', ['dev/bots/test.sh'], cwd=checkout)

    BuildExamples(api, git_hash)

    # TODO(yjbanov): we do not yet have Android devices hooked up, nor do we
    # support the Android emulator. For now, only run on iOS Simulator.
    if api.platform.is_mac:
      TestCreateAndLaunch(api)

    # TODO(eseidel): We only want to generate one copy of the docs at a time
    # otherwise multiple rsyncs could race, causing badness. We'll eventually
    # need both a lock on the bucket, as well as some assurance that we're
    # always moving the docs forward. Possibly by using a separate builder.
    # Until then, only generate on linux to reduce the chance of race.
    if api.platform.is_linux:
      GenerateDocs(api)


def GenTests(api):
  for platform in ('mac', 'linux'):
    test = (api.test(platform) + api.platform(platform, 64) +
        api.properties(clobber=''))

    if platform == 'mac':
      test += (
        api.step_data('enumerate_xcode_installations', api.json.output({
          'installations': {
            '/some/path': '7.2.1 build_number'
          }
        })) +
        api.step_data('set_xcode_version', api.json.output({}))
      )

    yield test

  yield (
    api.test('mac_cannot_find_xcode') +
    api.platform('mac', 64) +
    api.properties(clobber='') +
    api.step_data('enumerate_xcode_installations', api.json.output({
      'installations': {}
    }))
  )

# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from common.skia import global_constants


DEPS = [
  'ct',
  'file',
  'depot_tools/gclient',
  'gsutil',
  'recipe_engine/json',
  'recipe_engine/path',
  'recipe_engine/properties',
  'recipe_engine/step',
  'recipe_engine/time',
  'skia',
  'skia_swarming',
  'swarming',
  'swarming_client',
  'depot_tools/tryserver',
]


SKPS_VERSION_FILE = 'skps_version'
CT_SKPS_ISOLATE = 'ct_skps.isolate'

# Do not batch archive more slaves than this value. This is used to prevent
# no output timeouts in the 'isolate tests' step.
MAX_SLAVES_TO_BATCHARCHIVE = 100

TOOL_TO_DEFAULT_SKPS_PER_SLAVE = {
    'dm': 10000,
    'nanobench': 1000,
    'get_images_from_skps': 10000,
}

# The SKP repository to use.
DEFAULT_SKPS_CHROMIUM_BUILD = 'fad657e-276e633'


def RunSteps(api):
  # Figure out which repository to use.
  buildername = api.properties['buildername']
  if '10k' in buildername:
    ct_page_type = '10k'
    num_pages = 10000
  elif '100k' in buildername:
    ct_page_type = '100k'
    num_pages = 100000
  elif '1m' in buildername:
    ct_page_type = 'All'
    num_pages = 1000000
  else:
    raise Exception('Do not recognise the buildername %s.' % buildername)

  # Figure out which configuration to build.
  if 'Release' in buildername:
    configuration = 'Release'
  else:
    configuration = 'Debug'

  # Figure out which tool to use.
  if 'DM' in buildername:
    skia_tool = 'dm'
    build_target = 'dm'
  elif 'BENCH' in buildername:
    skia_tool = 'nanobench'
    build_target = 'nanobench'
  elif 'IMG_DECODE' in buildername:
    skia_tool = 'get_images_from_skps'
    build_target = 'tools'
  else:
    raise Exception('Do not recognise the buildername %s.' % buildername)

  # Checkout Skia and Chromium.
  gclient_cfg = api.gclient.make_config()

  skia = gclient_cfg.solutions.add()
  skia.name = 'skia'
  skia.managed = False
  skia.url = global_constants.SKIA_REPO
  skia.revision = (api.properties.get('parent_got_revision') or
                   api.properties.get('orig_revision') or
                   api.properties.get('revision') or
                   'origin/master')
  gclient_cfg.got_revision_mapping['skia'] = 'got_revision'

  src = gclient_cfg.solutions.add()
  src.name = 'src'
  src.managed = False
  src.url = 'https://chromium.googlesource.com/chromium/src.git'
  src.revision = 'origin/master'  # Always checkout Chromium at ToT.

  for repo in (skia, src):
    api.skia.update_repo(api.path['slave_build'], repo)

  update_step = api.gclient.checkout(gclient_config=gclient_cfg)
  skia_hash = update_step.presentation.properties['got_revision']

  # Checkout Swarming scripts.
  # Explicitly set revision to empty string to checkout swarming ToT. If this is
  # not done then it crashes due to missing
  # api.properties['parent_got_swarming_client_revision'] which seems to be
  # set only for Chromium bots.
  api.swarming_client.checkout(revision='')
  # Ensure swarming_client is compatible with what recipes expect.
  api.swarming.check_client_version()
  # Setup Go isolate binary.
  chromium_checkout = api.path['slave_build'].join('src')
  api.skia_swarming.setup_go_isolate(chromium_checkout.join('tools', 'luci-go'))

  # Apply issue to the Skia checkout if this is a trybot run.
  api.tryserver.maybe_apply_issue()

  # Build the tool.
  api.step('build %s' % build_target,
           ['make', build_target, 'BUILDTYPE=%s' % configuration],
           cwd=api.path['checkout'])

  skps_chromium_build = api.properties.get(
      'skps_chromium_build', DEFAULT_SKPS_CHROMIUM_BUILD)

  # Set build property to make finding SKPs convenient.
  api.step.active_result.presentation.properties['Location of SKPs'] = (
      'https://pantheon.corp.google.com/storage/browser/%s/swarming/skps/%s/%s/'
          % (api.ct.CT_GS_BUCKET, ct_page_type, skps_chromium_build))

  # Delete swarming_temp_dir to ensure it starts from a clean slate.
  api.file.rmtree('swarming temp dir', api.skia_swarming.swarming_temp_dir)

  num_per_slave = api.properties.get(
      'num_per_slave', TOOL_TO_DEFAULT_SKPS_PER_SLAVE[skia_tool])
  ct_num_slaves = api.properties.get('ct_num_slaves', num_pages / num_per_slave)

  # Try to figure out if the SKPs we are going to isolate already exist
  # locally by reading the SKPS_VERSION_FILE.
  download_skps = True
  expected_version_contents = {
      "chromium_build": skps_chromium_build,
      "page_type": ct_page_type,
      "num_slaves": ct_num_slaves,
  }
  skps_dir = api.path['slave_build'].join('skps')
  version_file = skps_dir.join(SKPS_VERSION_FILE)
  if api.path.exists(version_file):  # pragma: nocover
    version_file_contents = api.file.read(
        "Read %s" % version_file,
        version_file,
        test_data=expected_version_contents,
        infra_step=True)
    actual_version_contents = api.json.loads(version_file_contents)
    differences = (set(expected_version_contents.items()) ^
                   set(actual_version_contents.items()))
    download_skps = len(differences) != 0
    if download_skps:
      # Delete and recreate the skps dir.
      api.file.rmtree(api.path.basename(skps_dir), skps_dir)
      api.file.makedirs(api.path.basename(skps_dir), skps_dir)

  # If a blacklist file exists then specify SKPs to be blacklisted.
  blacklists_dir = api.path['slave_build'].join(
      'skia', 'infra', 'bots', 'ct', 'blacklists')
  blacklist_file = blacklists_dir.join(
      '%s_%s_%s.json' % (skia_tool, ct_page_type, skps_chromium_build))
  blacklist_skps = []
  if api.path.exists(blacklist_file):  # pragma: nocover
    blacklist_file_contents = api.file.read(
        "Read %s" % blacklist_file,
        blacklist_file,
        infra_step=True)
    blacklist_skps = api.json.loads(blacklist_file_contents)['blacklisted_skps']

  for slave_num in range(1, ct_num_slaves + 1):
    if download_skps:
      # Download SKPs.
      api.ct.download_swarming_skps(
          ct_page_type, slave_num, skps_chromium_build,
          api.path['slave_build'].join('skps'),
          start_range=((slave_num-1)*num_per_slave) + 1,
          num_skps=num_per_slave)

    # Create this slave's isolated.gen.json file to use for batcharchiving.
    isolate_dir = chromium_checkout.join('chrome')
    isolate_path = isolate_dir.join(CT_SKPS_ISOLATE)
    extra_variables = {
        'SLAVE_NUM': str(slave_num),
        'TOOL_NAME': skia_tool,
        'GIT_HASH': skia_hash,
        'CONFIGURATION': configuration,
        'BUILDER': buildername,
    }
    api.skia_swarming.create_isolated_gen_json(
        isolate_path, isolate_dir, 'linux', 'ct-%s-%s' % (skia_tool, slave_num),
        extra_variables, blacklist=blacklist_skps)

  if download_skps:
    # Since we had to download SKPs create an updated version file.
    api.file.write("Create %s" % version_file,
                   version_file,
                   api.json.dumps(expected_version_contents),
                   infra_step=True)

  # Batcharchive everything on the isolate server for efficiency.
  max_slaves_to_batcharchive = MAX_SLAVES_TO_BATCHARCHIVE
  if '1m' in buildername:
    # Break up the "isolate tests" step into batches with <100k files due to
    # https://github.com/luci/luci-go/issues/9
    max_slaves_to_batcharchive = 5
  tasks_to_swarm_hashes = []
  for slave_start_num in xrange(1, ct_num_slaves+1, max_slaves_to_batcharchive):
    m = min(max_slaves_to_batcharchive, ct_num_slaves)
    batcharchive_output = api.skia_swarming.batcharchive(
        targets=['ct-' + skia_tool + '-%s' % num for num in range(
            slave_start_num, slave_start_num + m)])
    tasks_to_swarm_hashes.extend(batcharchive_output)
  # Sort the list to go through tasks in order.
  tasks_to_swarm_hashes.sort()

  # Trigger all swarming tasks.
  dimensions={'os': 'Ubuntu-14.04', 'cpu': 'x86-64', 'pool': 'Chrome'}
  if 'GPU' in buildername:
    dimensions['gpu'] = '10de:104a'
  tasks = api.skia_swarming.trigger_swarming_tasks(
      tasks_to_swarm_hashes, dimensions=dimensions, io_timeout=40*60)

  # Now collect all tasks.
  failed_tasks = []
  for task in tasks:
    try:
      api.skia_swarming.collect_swarming_task(task)

      if skia_tool == 'nanobench':
        output_dir = api.skia_swarming.tasks_output_dir.join(
            task.title).join('0')
        utc = api.time.utcnow()
        gs_dest_dir = 'ct/%s/%d/%02d/%02d/%02d/' % (
            ct_page_type, utc.year, utc.month, utc.day, utc.hour)
        for json_output in api.file.listdir('output dir', output_dir):
          api.gsutil.upload(
              name='upload json output',
              source=output_dir.join(json_output),
              bucket='skia-perf',
              dest=gs_dest_dir,
              env={'AWS_CREDENTIAL_FILE': None, 'BOTO_CONFIG': None},
              args=['-R']
          )

    except api.step.StepFailure as e:
      failed_tasks.append(e)

  if failed_tasks:
    raise api.step.StepFailure(
        'Failed steps: %s' % ', '.join([f.name for f in failed_tasks]))


def GenTests(api):
  ct_num_slaves = 5
  num_per_slave = 10
  skia_revision = 'abc123'

  yield(
    api.test('CT_DM_10k_SKPs') +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_DM_10k_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

  yield(
    api.test('CT_IMG_DECODE_10k_SKPs') +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_IMG_DECODE_'
                    '10k_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

  yield(
    api.test('CT_DM_100k_SKPs') +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_DM_100k_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

  yield(
    api.test('CT_IMG_DECODE_100k_SKPs') +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_IMG_DECODE_'
                    '100k_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

  yield(
    api.test('CT_CPU_BENCH_10k_SKPs') +
    api.properties(
        buildername=
            'Perf-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Release-CT_BENCH_10k_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    ) +
    api.path.exists(
        api.path['slave_build'].join('skia'),
        api.path['slave_build'].join('src')
    )
  )

  yield(
    api.test('CT_GPU_BENCH_10k_SKPs') +
    api.properties(
        buildername=
            'Perf-Ubuntu-GCC-Golo-GPU-GT610-x86_64-Release-CT_BENCH_10k_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    ) +
    api.path.exists(
        api.path['slave_build'].join('skia'),
        api.path['slave_build'].join('src')
    )
  )

  yield(
    api.test('CT_DM_1m_SKPs') +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_DM_1m_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

  yield (
    api.test('CT_DM_SKPs_UnknownBuilder') +
    api.properties(
        buildername=
            'Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_DM_UnknownRepo_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    ) +
    api.expect_exception('Exception')
  )

  yield (
    api.test('CT_10k_SKPs_UnknownBuilder') +
    api.properties(
        buildername=
            'Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_UnknownTool_10k_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    ) +
    api.expect_exception('Exception')
  )

  yield(
    api.test('CT_DM_1m_SKPs_slave3_failure') +
    api.step_data('ct-dm-3 on Ubuntu-14.04', retcode=1) +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_DM_1m_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

  yield(
    api.test('CT_DM_1m_SKPs_2slaves_failure') +
    api.step_data('ct-dm-1 on Ubuntu-14.04', retcode=1) +
    api.step_data('ct-dm-3 on Ubuntu-14.04', retcode=1) +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_DM_1m_SKPs',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

  yield(
    api.test('CT_DM_10k_SKPs_Trybot') +
    api.properties(
        buildername=
            'Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_DM_10k_SKPs-Trybot',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        rietveld='codereview.chromium.org',
        issue=1499623002,
        patchset=1,
    )
  )

  yield(
    api.test('CT_IMG_DECODE_10k_SKPs_Trybot') +
    api.properties(
        buildername='Test-Ubuntu-GCC-GCE-CPU-AVX2-x86_64-Debug-CT_IMG_DECODE_'
                    '10k_SKPs_Trybot',
        ct_num_slaves=ct_num_slaves,
        num_per_slave=num_per_slave,
        revision=skia_revision,
    )
  )

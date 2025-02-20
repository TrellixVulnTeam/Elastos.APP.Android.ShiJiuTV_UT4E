# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from recipe_engine.recipe_api import Property


DEPS = [
  'recipe_engine/properties',
  'recipe_engine/python',
  'recipe_engine/raw_io',
  'recipe_engine/step',
]

PROPERTIES = {
  'gerrit': Property(kind=str, help='Gerrit host', default=None,
                     param_name='gerrit_host'),
  'patch_project': Property(kind=str, help='Gerrit project', default=None,
                            param_name='gerrit_project'),
  'event.patchSet.ref': Property(kind=str, help='Gerrit patch ref',
                                 default=None, param_name='gerrit_patch_ref'),
  'repository': Property(kind=str, help='Full url to a Git repository',
                         default=None, param_name='repo_url'),
  'refspec': Property(kind=str, help='Refspec to checkout', default='master'),
  'category': Property(kind=str, help='Build category', default=None),
}


def RunSteps(api, category, repo_url, refspec, gerrit_host, gerrit_project,
             gerrit_patch_ref):
  if category == 'cq':
    assert gerrit_host.startswith('https://')
    repo_url = '%s/%s' % (gerrit_host.rstrip('/'), gerrit_project)
    refspec = gerrit_patch_ref

  assert repo_url and refspec, 'repository url and refspec must be given'
  assert repo_url.startswith('https://')

  api.step('git init', ['git', 'init'])
  api.step('git reset', ['git', 'reset', '--hard'])
  api.step('git fetch', ['git', 'fetch', repo_url, '%s' % refspec])
  api.step('git checkout', ['git', 'checkout', 'FETCH_HEAD'])
  api.step('git submodule update', ['git', 'submodule', 'update',
                                    '--init', '--recursive'])
  result = api.python.inline(
      'read tests',
      # Multiplatform "cat"
      "with open('infra/config/ci.cfg') as f: print f.read()",
           stdout=api.raw_io.output(),
           step_test_data=(lambda:
             api.raw_io.test_api.stream_output(
               './a.sh\npython b.py\npython c.py args')))

  tests = []
  for l in result.stdout.splitlines():
    l = l.strip()
    if l and not l.startswith('#'):
      tests.append(l)

  with api.step.defer_results():
    for l in sorted(tests):
      name = 'test: %s' % l
      cmd = l.split()
      if cmd[0] == 'python' and len(cmd) >= 2:
        api.python(name, script=cmd[1], args=cmd[2:])
      else:
        api.step(name, cmd)


def GenTests(api):
  yield api.test('ci') + api.properties(
      repository='https://chromium.googlesource.com/infra/infra',
  )
  yield api.test('cq_try') + api.properties.tryserver_gerrit(
      full_project_name='infra/infra',
  )
  yield api.test('ci_fail_but_run_all') + api.properties(
      repository='https://chromium.googlesource.com/infra/infra',
      refspec='release-52'
  ) + api.override_step_data('test: ./a.sh', retcode=1)

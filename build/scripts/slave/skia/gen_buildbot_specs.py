#!/usr/bin/env python
#
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


'''Generate buildbot specs for all buildbots.'''


import datetime
import imp
import json
import os
import re
import subprocess
import sys
import tempfile


SKIA_RECIPES = [
  'swarm_compile.py',
  'swarm_housekeeper.py',
  'swarm_perf.py',
  'swarm_test.py',
  'swarm_trigger.py'
]


def prettier_print(obj, indent, stream=sys.stdout, max_line_length=80):
  """Pretty-print the object, in a nicer format than pprint."""

  def _breakline(line):
    """Break the line to fit under N characters."""
    # If we're under the limit, just return.
    if len(line) <= max_line_length:
      return [line]

    # Dict entries.
    m = re.match(r'^(\s+)(.+): (.+)$', line)
    if m:
      return (_breakline(m.groups()[0] + m.groups()[1] + ':') +
              _breakline(m.groups()[0] + '    ' + m.groups()[2]))

    # List entries and dict keys.
    m = re.match(r"^(\s+)'(.+)'([:,])$", line)
    if m:
      prefix = m.groups()[0]
      content = m.groups()[1]
      max_len = max_line_length - len(prefix) - len("(''):")
      parts = []
      while len(content) > max_len:
        parts.append(content[:max_len])
        content = content[max_len:]
      parts.append(content)
      lines = _breakline(prefix + "('" + parts[0] + "'")
      for p in parts[1:-1]:
        lines.extend(_breakline(prefix + " '" + p + "'"))
      lines.extend(_breakline(prefix + " '" + parts[-1] + "')" + m.groups()[2]))
      return lines

  class LineBreakingStream(object):
    """Stream wrapper which writes line-by-line, breaking them as needed."""
    def __init__(self, backing_stream):
      self._backing_stream = backing_stream
      self._current_line = ''

    def _writeline(self, line):
      for l in _breakline(line):
        self._backing_stream.write(l + '\n')

    def write(self, s):
      self._current_line += s
      split = self._current_line.split('\n')
      for w in split[:-1]:
        self._writeline(w)
      self._current_line = split[len(split)-1]

    def flush(self):
      self._writeline(self._current_line)

  def _pprint(obj, indent, stream):
    indent_str = ' ' * indent
    if isinstance(obj, dict):
      stream.write('{\n')
      for k in sorted(obj.iterkeys()):
        stream.write(indent_str + '\'%s\': ' % k)
        _pprint(obj[k], indent + 2, stream=stream)
        stream.write(',\n')
      stream.write(' ' * (indent-2) + '}')
    elif isinstance(obj, list):
      stream.write('[\n')
      for v in obj:
        stream.write(indent_str)
        _pprint(v, indent + 2, stream=stream)
        stream.write(',\n')
      stream.write(' ' * (indent-2) + ']')
    elif isinstance(obj, basestring):
      stream.write('\'%s\'' % obj)
    elif isinstance(obj, bool):
      if obj:
        stream.write('True')
      else:
        stream.write('False')
    else:
      stream.write(obj)

  s = LineBreakingStream(stream)
  _pprint(obj, indent, stream=s)
  s.flush()


def get_bots():
  """Find all of the bots referenced in Skia recipes."""
  cwd = os.path.realpath(os.path.dirname(__file__))
  bots = []
  for skia_recipe in SKIA_RECIPES:
    skia_recipe = os.path.join(cwd, os.pardir, 'recipes', 'skia', skia_recipe)
    skia = imp.load_source('skia', skia_recipe)
    for _, slaves in skia.TEST_BUILDERS.iteritems():
      for _, builders in slaves.iteritems():
        bots.extend(builders)
  bots.sort()
  return bots


def main(buildbot_spec_path):
  """Generate a spec for each of the above bots. Dump them all to a file."""
  # Get the list of bots.
  bots = get_bots()

  # Create the fake specs.
  specs = {}
  tmp_spec_file = tempfile.NamedTemporaryFile(delete=False)
  tmp_spec_file.close()
  try:
    for bot in bots:
      subprocess.check_call(['python', buildbot_spec_path,
                             tmp_spec_file.name, bot])
      with open(tmp_spec_file.name) as f:
        spec = json.load(f)
      spec['dm_flags'] = ['--dummy-flags']
      spec['nanobench_flags'] = ['--dummy-flags']
      specs[bot] = spec
  finally:
    os.remove(tmp_spec_file.name)

  out = os.path.realpath(os.path.join(
      os.path.dirname(os.path.realpath(__file__)), os.pardir,
      'recipe_modules', 'skia', 'fake_specs.py'))

  with open(out, 'w') as f:
    f.write('''# This file is generated by the %s script.

FAKE_SPECS = ''' % sys.argv[0])
    prettier_print(specs, indent=2, stream=f)

  print 'Wrote output to %s' % out


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print >> sys.stderr, ('Usage: %s <path_to_buildbot_spec_script>'
                          % sys.argv[0])
    sys.exit(1)
  main(*sys.argv[1:])

#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
This tool creates a tarball with all the sources, but without .git directories.

It can also remove files which are not strictly required for build, so that
the resulting tarball can be reasonably small (last time it was ~110 MB).

Example usage:

export_tarball.py /foo/bar

The above will create file /foo/bar.tar.bz2.
"""

import optparse
import os
import subprocess
import sys
import tarfile


NONESSENTIAL_DIRS = (
    'chrome/common/extensions/docs',
    'third_party/findbugs',
    'third_party/hunspell_dictionaries',
    'third_party/hunspell/tests',
    'third_party/sqlite/src/test',
    'third_party/xdg-utils/tests',
    'third_party/yasm/source/patched-yasm/modules/arch/x86/tests',
    'third_party/yasm/source/patched-yasm/modules/dbgfmts/dwarf2/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/bin/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/coff/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/elf/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/macho/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/rdf/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/win32/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/win64/tests',
    'third_party/yasm/source/patched-yasm/modules/objfmts/xdf/tests',
    'third_party/WebKit/LayoutTests',
    'third_party/WebKit/Tools/Scripts',
    'tools/gyp/test',
    'v8/test',
)

ESSENTIAL_FILES = (
    'chrome/test/data/webui/i18n_process_css_test.html',
)

TEST_DIRS = (
    'breakpad/src/processor/testdata',
    'chrome/test/data',
    'content/test/data',
    'courgette/testdata',
    'media/test/data',
    'native_client/src/trusted/service_runtime/testdata',
    'net/data',
)


# Workaround lack of the exclude parameter in add method in python-2.4.
# TODO(phajdan.jr): remove the workaround when it's not needed on the bot.
class MyTarFile(tarfile.TarFile):
  def set_remove_nonessential_files(self, remove):
    self.__remove_nonessential_files = remove

  def set_verbose(self, verbose):
    self.__verbose = verbose

  def set_src_dir(self, src_dir):
    self.__src_dir = src_dir

  def __report_skipped(self, name):
    if self.__verbose:
      print 'D\t%s' % name

  def __report_added(self, name):
    if self.__verbose:
      print 'A\t%s' % name

  def add(self, name, arcname=None, recursive=True, exclude=None, filter=None):
    _, file_name = os.path.split(name)
    if file_name in ('.git', 'out'):
      self.__report_skipped(name)
      return

    if self.__remove_nonessential_files:
      # WebKit change logs take quite a lot of space. This saves ~10 MB
      # in a bzip2-compressed tarball.
      if 'ChangeLog' in name:
        self.__report_skipped(name)
        return

      # Preserve GYP/GN files, and other potentially critical files, so that
      # build/gyp_chromium / gn gen can work.
      rel_name = os.path.relpath(name, self.__src_dir)
      keep_file = ('.gyp' in file_name or
                   '.gn' in file_name or
                   '.isolate' in file_name or
                   '.grd' in file_name or
                   rel_name in ESSENTIAL_FILES)

      # Remove contents of non-essential directories.
      if not keep_file:
        for nonessential_dir in (NONESSENTIAL_DIRS + TEST_DIRS):
          if rel_name.startswith(nonessential_dir) and os.path.isfile(name):
            self.__report_skipped(name)
            return

    self.__report_added(name)
    tarfile.TarFile.add(self, name, arcname=arcname, recursive=recursive)


def main(argv):
  parser = optparse.OptionParser()
  parser.add_option("--basename")
  parser.add_option("--remove-nonessential-files",
                    dest="remove_nonessential_files",
                    action="store_true", default=False)
  parser.add_option("--test-data", action="store_true")
  # TODO(phajdan.jr): Remove --xz option when it's not needed for compatibility.
  parser.add_option("--xz", action="store_true")
  parser.add_option("--verbose", action="store_true", default=False)
  parser.add_option("--progress", action="store_true", default=False)
  parser.add_option("--src-dir")

  options, args = parser.parse_args(argv)

  if len(args) != 1:
    print 'You must provide only one argument: output file name'
    print '(without .tar.xz extension).'
    return 1

  if not os.path.exists(options.src_dir):
    print 'Cannot find the src directory ' + options.src_dir
    return 1

  # These two commands are from src/DEPS; please keep them in sync.
  if subprocess.call(['python', 'build/util/lastchange.py', '-o',
                      'build/util/LASTCHANGE'], cwd=options.src_dir) != 0:
    print 'Could not run build/util/lastchange.py to update LASTCHANGE.'
    return 1
  if subprocess.call(['python', 'build/util/lastchange.py', '-s',
                      'third_party/WebKit', '-o',
                      'build/util/LASTCHANGE.blink'],
                     cwd=options.src_dir) != 0:
    print 'Could not run build/util/lastchange.py to update LASTCHANGE.blink.'
    return 1

  output_fullname = args[0] + '.tar'
  output_basename = options.basename or os.path.basename(args[0])

  archive = MyTarFile.open(output_fullname, 'w')
  archive.set_remove_nonessential_files(options.remove_nonessential_files)
  archive.set_verbose(options.verbose)
  archive.set_src_dir(options.src_dir)
  try:
    if options.test_data:
      for directory in TEST_DIRS:
        archive.add(os.path.join(options.src_dir, directory),
                    arcname=os.path.join(output_basename, directory))
    else:
      archive.add(options.src_dir, arcname=output_basename)
  finally:
    archive.close()

  if options.progress:
    sys.stdout.flush()
    pv = subprocess.Popen(
        ['pv', '--force', output_fullname],
        stdout=subprocess.PIPE,
        stderr=sys.stdout)
    with open(output_fullname + '.xz', 'w') as f:
      rc = subprocess.call(['xz', '-9', '-'], stdin=pv.stdout, stdout=f)
    pv.wait()
  else:
    rc = subprocess.call(['xz', '-9', output_fullname])

  if rc != 0:
    print 'xz -9 failed!'
    return 1

  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))

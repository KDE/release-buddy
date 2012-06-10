# Part of Release Buddy: Package Command

import re
import shutil
from buddylib import *

#
# Copyright (c) 2012 Allen Winter <winter@kde.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

def buddy_pack(options, project, branch):      
    return package(options, project['name'], project['desc'], branch)
  
def package(options, name, desc, version):
  archive = name + '-' + version + ".tar"

  desc = re.sub('^"', '',desc)
  desc = re.sub('"$', '',desc)
  desc = desc.replace('"', '\\\"')

  #TODO read the option EXTRA_IGNORES

  #write the CPack configfile for this project
  cpackcfg = options.Tarballs + os.sep + "CPackConfig.cmake"
  if not options.dryrun:
    writeCPackConfig(cpackcfg, name, desc, version, options.Sources)

  #generate the CPack command line
  args = createCPackCommand(options)

  #start logging this command
  outlines = ''
  outlines = outlines + "Begin Packaging " + name + "\n"
  Logger(options, outlines)

  ChangeDir(options, options.Tarballs)

  #clean possible archive junk left over from previous runs
  if os.path.exists(archive):
      os.remove(archive)
  if os.path.exists(archive + ".bz2"):
      os.remove(archive + ".bz2")
  if os.path.exists(archive + ".xz"):
      os.remove(archive + ".xz")

  #run the CPack command
  RUNIT(options, "cpack", args)

  #CPack doesn't have an LZMA generator, so we must bunzip2 then run xz ourselves.
  RUNIT(options, "bunzip2", archive + ".bz2")
  RUNIT(options, "xz", archive)

  #remove the CPack configfile
  if not options.dryrun:
    os.remove(cpackcfg)

  #remove CPack temporary files
  shutil.rmtree("_CPack_Packages", True)

  #finish logging this command
  outlines = ''
  outlines = outlines + "Packaging Complete\n"
  outlines = outlines + makeASubLine() + "\n"
  Logger(options, outlines)

def writeCPackConfig(f, name, desc, version, srcpath):
  try:
    of = open(f, "w")
  except IOError:
    fail("Unable to write CPackConfig.cmake, \"" + f + "\"")

  of.write("set(CPACK_GENERATOR \"TBZ2\")\n")
  of.write("set(CPACK_SOURCE_GENERATOR \"TBZ2\")\n")
  of.write("set(CPACK_PACKAGE_VENDOR \"The KDE Community\")\n")

  n = version.split('.')[0]
  of.write("set(CPACK_PACKAGE_VERSION_MAJOR " + n + ")\n")
  n = version.split('.')[1]
  of.write("set(CPACK_PACKAGE_VERSION_MINOR " + n + ")\n")
  n = version.split('.')[2]
  of.write("set(CPACK_PACKAGE_VERSION_PATCH " + n + ")\n")

  of.write("set(CPACK_PACKAGE_VERSION "
            "\"${CPACK_PACKAGE_VERSION_MAJOR}."
            "${CPACK_PACKAGE_VERSION_MINOR}."
            "${CPACK_PACKAGE_VERSION_PATCH}\")\n")

  of.write("set(CPACK_IGNORE_FILES \"/\\\\.git/\" \"/\\\\.gitignore\" \"/\\\\.svn/\"")
  of.write(" ${EXTRA_IGNORES})\n")

  of.write("set(CPACK_PACKAGE_NAME \"" + name + "\")\n")
  of.write("set(CPACK_PACKAGE_DESCRIPTION \"" + desc + "\")\n")

  of.write("set(CPACK_INSTALLED_DIRECTORIES \"")
  of.write(srcpath + os.sep + name)
  of.write(";.\")\n")

  of.write("set(CPACK_PACKAGE_FILE_NAME \"${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}\")\n")

  of.close()

def createCPackCommand(options):
  args = "-G TBZ2"
  if options.Verbose:
    args = args + " --verbose"
  return args
